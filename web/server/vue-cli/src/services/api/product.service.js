import ServiceClient from "@cc/prod";
import { BaseService } from "./_base.service";

class ProductsService extends BaseService {
  constructor() {
    super("v6/Products", ServiceClient);
  }
}

const prodService = new ProductsService();

export default prodService;
