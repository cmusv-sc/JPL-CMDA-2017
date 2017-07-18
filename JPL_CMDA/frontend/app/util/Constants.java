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

public class Constants {

	// API 1.3 URL
	public static final String NEW_API_URL = "http://localhost:9033/";

	// API Call format
	public static final String FORMAT = "json";
	
	// climate service
	public static final String NEW_GET_CLIMATE_SERVICE = "getAllClimateServices/";
	public static final String NEW_ADD_CLIMATE_SERVICE = "addClimateService";
	public static final String NEW_DELETE_CLIMATE_SERVICE = "climateService/deleteClimateService/id/";
	public static final String NEW_EDIT_CLIMATE_SERVICE = "updateClimateService";
	
	//service log
	public static final String NEW_GET_A_SERVICE_LOG = "getServiceExecutionLogs/";

    public static final String GET_DATASETLIST ="getDatasetList/";

	//New backend API (MySQL database)
	public static final String NEW_BACKEND = "http://localhost:9034/";
	//New service execution log stuff
	public static final String SERVICE_EXECUTION_LOG =	"serviceExecutionLog/";
	public static final String SERVICE_EXECUTION_LOG_QUERY =	"queryServiceExecutionLogs";
	public static final String SERVICE_EXECUTION_LOG_GET= "getServiceExecutionLog/";
	public static final String NEW_GET_ALL_SERVICE_LOG = "getAllServiceExecutionLog";

	//ServiceConfigItem
	public static final String CONFIG_ITEM =	"serviceConfigurationItem/";
	public static final String GET_CONFIG_ITEMS_BY_CONFIG= "serviceConfigurationItemByServiceConfig/";



}
