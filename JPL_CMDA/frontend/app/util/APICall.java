/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package util;

import play.Logger;
import play.libs.Json;
import play.libs.WS;
import play.libs.F.Function;
import play.libs.F.Promise;
import scala.Console;
import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.databind.node.ObjectNode;

public class APICall {
	public static enum ResponseType {
		SUCCESS, GETERROR, SAVEERROR, DELETEERROR, RESOLVEERROR, TIMEOUT, CONVERSIONERROR, UNKNOWN
	}

	public static JsonNode callAPI(String apiString) {
		Logger.info(apiString);
		Promise<WS.Response> responsePromise = WS
				.url(apiString).get();
		final Promise<JsonNode> bodyPromise = responsePromise
				.map(new Function<WS.Response, JsonNode>() {
					@Override
					public JsonNode apply(WS.Response response)
							throws Throwable {
						if (response.getStatus() == 200
								|| response.getStatus() == 201) {
							return response.asJson();
						} else {
							Logger.info(""+response.getStatus());
							return createResponse(ResponseType.GETERROR);
						}
					}
				});

		try {
			return bodyPromise.get(10000L);
		} catch (Exception e) {
			return createResponse(ResponseType.TIMEOUT);
		}

	}
	
	public static JsonNode callAPIParameter(String apiString, String paraName, String para) {
		Promise<WS.Response> responsePromise = WS
				.url(apiString).setQueryParameter(paraName, para).get();
		Console.print(responsePromise.get());
		final Promise<JsonNode> bodyPromise = responsePromise
				.map(new Function<WS.Response, JsonNode>() {
					@Override
					public JsonNode apply(WS.Response response)
							throws Throwable {
						if (response.getStatus() == 200
								|| response.getStatus() == 201) {
							return response.asJson();
						} else {
							Logger.info(""+response.getStatus());
							return createResponse(ResponseType.GETERROR);
						}
					}
				});

		try {
			return bodyPromise.get(10000L);
		} catch (Exception e) {
			return createResponse(ResponseType.TIMEOUT);
		}

	}

	public static JsonNode postAPI(String apiString, JsonNode jsonData) {
		Promise<WS.Response> responsePromise = WS.url(apiString).post(jsonData);
		final Promise<JsonNode> bodyPromise = responsePromise
				.map(new Function<WS.Response, JsonNode>() {
					@Override
					public JsonNode apply(WS.Response response)
							throws Throwable {
						if ((response.getStatus() == 201 || response
								.getStatus() == 200)) {
							try {
								return response.asJson();
							}
							catch (Exception e){
								return createResponse(ResponseType.SUCCESS);
							}
						} else {
							return createResponse(ResponseType.SAVEERROR);
						}
					}
				});
		try {
			return bodyPromise.get(10000L);
		} catch (Exception e) {
			return createResponse(ResponseType.TIMEOUT);
		}
	}

	public static JsonNode putAPI(String apiString, JsonNode jsonData) {
		Promise<WS.Response> responsePromise = WS.url(apiString).put(jsonData);
		final Promise<JsonNode> bodyPromise = responsePromise
				.map(new Function<WS.Response, JsonNode>() {
					@Override
					public JsonNode apply(WS.Response response)
							throws Throwable {
						if ((response.getStatus() == 201 || response
								.getStatus() == 200)
								&& !response.getBody().contains("not")) {
							return createResponse(ResponseType.SUCCESS);
						} else { 
							return createResponse(ResponseType.SAVEERROR);
						}
					}
				});
		try {
			return bodyPromise.get(10000L);
		} catch (Exception e) {
			return createResponse(ResponseType.TIMEOUT);
		}
	}
	
	public static JsonNode deleteAPI(String apiString) {
		Promise<WS.Response> responsePromise = WS.url(apiString.replace("+", "%20")).setContentType("text/html").delete();
		final Promise<JsonNode> bodyPromise = responsePromise
				.map(new Function<WS.Response, JsonNode>() {
					@Override
					public JsonNode apply(WS.Response response)
							throws Throwable {
						if ((response.getStatus() == 200 || response
								.getStatus() == 201)
								&& !response.getBody().contains("not")) {
							return createResponse(ResponseType.SUCCESS);
						} else {
							return createResponse(ResponseType.DELETEERROR);
						}
					}
				});
		try {
			return bodyPromise.get(10000L);
		} catch (Exception e) {
			return createResponse(ResponseType.TIMEOUT);
		}

	}

	public static JsonNode createResponse(ResponseType type) {
		ObjectNode jsonData = Json.newObject();
		switch (type) {
		case SUCCESS:
			jsonData.put("success", "Success!");
			break;
		case GETERROR:
			jsonData.put("error", "Cannot get data from server");
			break;
		case SAVEERROR:
			jsonData.put("error", "Cannot be saved. The data must be invalid!");
			break;
		case DELETEERROR:
			jsonData.put("error", "Cannot be deleted on server");
			break;
		case RESOLVEERROR:
			jsonData.put("error", "Cannot be resolved on server");
			break;
		case TIMEOUT:
			jsonData.put("error", "No response/Timeout from server");
			break;
		case CONVERSIONERROR:
			jsonData.put("error", "Conversion error");
			break;
		default:
			jsonData.put("error", "Unknown errors");
			break;
		}
		return jsonData;
	}
}