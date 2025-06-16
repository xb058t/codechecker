import mitt from "mitt";
import {
  TBufferedTransport,
  TJSONProtocol,
  createXHRClient,
  createXHRConnection
} from "thrift";

import router from "@/router";
import store from "@/store";
import { ADD_ERROR, PURGE_AUTH } from "@/store/mutations.type";
import authService from "./auth.service";

const host = window.location.hostname;
const port = undefined;

const eventHub = mitt();

class BaseService {
  constructor(serviceName, serviceClass, apiPrefix = "v6", isProductScoped = false) {
  this._serviceName = serviceName;
  this._serviceClass = serviceClass;
  this._apiPrefix = apiPrefix;
  this._isProductScoped = isProductScoped;

  this._client = null;
  this._currentEndpoint = window.__cc_endpoint || null;

  eventHub.on("update", endpoint => {
    console.log("[BaseService] update received:", endpoint);
    this._currentEndpoint = endpoint;
    window.__cc_endpoint = endpoint;
    this._client = null;
  });
}

getClient() {
  if (this._isProductScoped) {
    const endpoint = router.currentRoute.value.params?.endpoint;
    if (!endpoint) {
      console.warn("[BaseService] No endpoint found in route params!");
    }
    this._currentEndpoint = endpoint || "";
  }

  if (!this._client) {
    this._client = this.createClient(this._currentEndpoint);
  }
  return this._client;
}


  getCurrentProduct() {
    const endpoint = router.currentRoute.value.params?.endpoint;
    console.log("TEST CURRENT:", endpoint);
    return endpoint;
  }

  createClient(productEndpoint = "") {
    const prefix = this._isProductScoped && productEndpoint
    ? `/${productEndpoint}/${this._apiPrefix}`
    : `/${this._apiPrefix}`;
    const finalPath = `${prefix}/${this._serviceName}`;
    console.log("[Thrift] final path:", finalPath);

    const connection = createXHRConnection(host, port, {
      transport: TBufferedTransport,
      protocol: TJSONProtocol,
      path: finalPath,
      https: window.location.protocol === "https:"
    });

    const getXmlHttpRequestObject = connection.getXmlHttpRequestObject;
    connection.getXmlHttpRequestObject = function () {
      const xreq = getXmlHttpRequestObject();

      xreq.addEventListener("readystatechange", function () {
        if (this.readyState === 1) {
          const token = authService.getToken();
          if (token) {
            xreq.setRequestHeader("Authorization", "Bearer " + token);
          }

        } else if (this.readyState === 4) {
          if (this.status === 504) {
            store.commit(ADD_ERROR, `Error ${this.status}: ${this.statusText}`);
          } else if (this.status === 401) {
            store.commit(PURGE_AUTH);
          }
        }
      });

      return xreq;
    };

    return createXHRClient(this._serviceClass, connection);
  }
}

const handleThriftError = function (cb, onError) {
  return (err, ...args) => {
    if (!err) {
      if (cb) cb.apply(this, args);
      return;
    }

    if (err instanceof Error) {
      const msg = err.message;
      if (msg.includes("Error code 401:")) {
        store.commit(PURGE_AUTH);
        router
          .push({
            name: "login",
            query: { return_to: router.currentRoute.fullPath }
          })
          .catch(() => {});
        // if (onError) onError(err);
        return;
      } else if (msg.match(/The product .* does not exist!/)) {
        router.replace({ name: "404" }).catch(() => {});
        return;
      }
    }

    if (onError) {
      onError(err);
    } else if (err instanceof Error) {
      console.error("[Thrift Error]", err);
      store.commit(ADD_ERROR, err.message);
    }
  };
};

export {
  eventHub,
  handleThriftError,
  BaseService
};
