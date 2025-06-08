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

// Host should be set explicitly to `hostname` because thrift will use
// the value of `window.location.host` which will contain port number by
// default on local host which cause invalid url format.
const host = process.env.CC_SERVER_HOST || window.location.hostname;
const port = parseInt(process.env.CC_SERVER_PORT, 10) ||
  parseInt(window.location.port, 10);
const api = process.env.CC_API_VERSION;

const eventHub = mitt();

class BaseService {
  constructor(serviceName, serviceClass) {
    this._serviceName = serviceName;
    this._serviceClass = serviceClass;
    this._client = this.createClient();

    eventHub.on("update", endpoint => {
      this._client = this.createClient(endpoint);
    });
  }

  getClient() {
    return this._client;
  }

  createClient(endpoint) {
    const productEndpoint = endpoint ? "/" + endpoint : "";
    const connection = createXHRConnection(host, port, {
      transport: TBufferedTransport,
      protocol: TJSONProtocol,
      path: `${productEndpoint}/v${api}/${this._serviceName}`,
      https: window.location.protocol === "https:"
    });

    const getXmlHttpRequestObject = connection.getXmlHttpRequestObject;
    connection.getXmlHttpRequestObject = function () {
      const xreq = getXmlHttpRequestObject();

      xreq.addEventListener("readystatechange", function () {
        if (this.readyState === 1) {
          xreq.setRequestHeader(
            "Authorization",
            "Bearer " + authService.getToken()
          );
        } else if (this.readyState === 4) {
          if (this.status === 504) {
            store.commit(
              ADD_ERROR,
              `Error ${this.status}: ${this.statusText}`
            );
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
      if (msg.indexOf("Error code 401:") !== -1) {
        store.commit(PURGE_AUTH);
        router
          .push({
            name: "login",
            query: { return_to: router.currentRoute.fullPath }
          })
          .catch(() => {});
        if (onError) onError(err);
        return;
      } else if (
        msg.search(/The product .* does not exist!/) > -1
      ) {
        router.replace({ name: "404" }).catch(() => {});
        return;
      }
    }

    if (onError) {
      onError(err);
    } else if (err instanceof Error) {
      store.commit(ADD_ERROR, err.message);
    }
  };
};

export {
  eventHub,
  handleThriftError,
  BaseService
};
  