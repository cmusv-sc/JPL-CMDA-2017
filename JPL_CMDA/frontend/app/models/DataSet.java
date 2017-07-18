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

package models;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import util.APICall;
import util.Constants;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

public class DataSet {

	private String id;
	private String dataSetName;
	private String agencyId;
	private String instrument;
	private String physicalVariable;
	private String CMIP5VarName;
	private String units;
	private String gridDimension;
	private String source;
	private String status;
	private String ResponsiblePerson;
	private String comments;
	private String dataSourceName;
	private String variableName;
	private String dataSourceInput;
	private String variableNameInput;
	private String startTime;
	private String endTime;
	
	public String getStartTime() {
		return startTime;
	}
	
	public String getEndTime() {
		return endTime;
	}
	
	public void setEndTime(String dataSetEndTime) {
		this.endTime = dataSetEndTime;
	}
	
	public void setStartTime(String dataSetStartTime) {
		this.startTime = dataSetStartTime;
	}
	
	public String getDataSetName() {
		return dataSetName;
	}
	public void setDataSetName(String dataSetName) {
		this.dataSetName = dataSetName;
	}
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	public String getAgencyId() {
		return agencyId;
	}
	public void setAgencyId(String agencyId) {
		this.agencyId = agencyId;
	}
	public String getInstrument() {
		return instrument;
	}
	public void setInstrument(String instrument) {
		this.instrument = instrument;
	}
	public String getPhysicalVariable() {
		return physicalVariable;
	}
	public void setPhysicalVariable(String physicalVariable) {
		this.physicalVariable = physicalVariable;
	}
	public String getCMIP5VarName() {
		return CMIP5VarName;
	}
	public void setCMIP5VarName(String cMIP5VarName) {
		CMIP5VarName = cMIP5VarName;
	}
	public String getUnits() {
		return units;
	}
	public void setUnits(String units) {
		this.units = units;
	}
	public String getGridDimension() {
		return gridDimension;
	}
	public void setGridDimension(String gridDimension) {
		this.gridDimension = gridDimension;
	}
	public String getSource() {
		return source;
	}
	public void setSource(String source) {
		this.source = source;
	}
	public String getStatus() {
		return status;
	}
	public void setStatus(String status) {
		this.status = status;
	}
	public String getResponsiblePerson() {
		return ResponsiblePerson;
	}
	public void setResponsiblePerson(String responsiblePerson) {
		ResponsiblePerson = responsiblePerson;
	}
	public String getComments() {
		return comments;
	}
	public void setComments(String comments) {
		this.comments = comments;
	}
	public String getDataSourceName() {
		return dataSourceName;
	}
	public void setDataSourceName(String dataSourceName) {
		this.dataSourceName = dataSourceName;
	}
	public String getVariableName() {
		return variableName;
	}
	public void setVariableName(String variableName) {
		this.variableName = variableName;
	}
	public String getDataSourceInput() {
		return dataSourceInput;
	}
	public void setDataSourceInput(String dataSourceInput) {
		this.dataSourceInput = dataSourceInput;
	}
	public String getVariableNameInput() {
		return variableNameInput;
	}
	public void setVariableNameInput(String variableNameInput) {
		this.variableNameInput = variableNameInput;
	}
	
	private static final String GET_ALL_DATASET = Constants.NEW_BACKEND + "dataset/getAllDatasets/json";
	private static final String DATASET_QUERY = Constants.NEW_BACKEND + "dataset/queryDataset";
	
	public static List<DataSet> all() {

		List<DataSet> dataSets = new ArrayList<DataSet>();

		JsonNode dataSetNode = APICall.callAPI(GET_ALL_DATASET);

		if (dataSetNode == null || dataSetNode.has("error")
				|| !dataSetNode.isArray()) {
			return dataSets;
		}

		for (int i = 0; i < dataSetNode.size(); i++) {
			JsonNode json = dataSetNode.path(i);
			DataSet dataset = new DataSet();
			dataset.setId(json.get("id").asText());
			dataset.setDataSetName(json.get("name").asText());
			dataset.setAgencyId(json.get("agencyId").asText());
			dataset.setInstrument(json.get("instrument").get("name").asText());
			dataset.setPhysicalVariable(json.get("physicalVariable").asText());
			dataset.setCMIP5VarName(json.get("CMIP5VarName").asText());
			dataset.setUnits(json.get("units").asText());
			dataset.setGridDimension(json.get("gridDimension").asText());
			dataset.setSource(json.get("source").asText());
			dataset.setStatus(json.get("status").asText());
			dataset.setResponsiblePerson(json.get("responsiblePerson").asText());
			dataset.setDataSourceName(json.get("dataSourceNameinWebInterface").asText());
			dataset.setVariableName(json.get("variableNameInWebInterface").asText());
			dataset.setDataSourceInput(json.get("dataSourceInputParameterToCallScienceApplicationCode").asText());
			dataset.setVariableNameInput(json.get("variableNameInputParameterToCallScienceApplicationCode").asText());
			String startTime = json.findPath("startTime").asText();
			String endTime = json.findPath("endTime").asText();
			Date tmpTime = null;
			
			try {
				tmpTime = (new SimpleDateFormat("MMM dd, yyyy hh:mm:ss a")).parse(startTime);
				
				if (tmpTime != null) {
					dataset.setStartTime(new SimpleDateFormat("YYYYMM").format(tmpTime));
				}
		    } catch (ParseException e){	    

		    }
			
			try {
				tmpTime = (new SimpleDateFormat("MMM dd, yyyy hh:mm:ss a")).parse(endTime);
				
				if (tmpTime != null) {
					dataset.setEndTime(new SimpleDateFormat("YYYYMM").format(tmpTime));
				}
		    } catch (ParseException e){	    

		    }
			dataSets.add(dataset);
		}
		return dataSets;
	}
	
public static List<DataSet> queryDataSet(String dataSetName, String agency, String instrument, String physicalVariable, String gridDimension, Date dataSetStartTime, Date dataSetEndTime) {
		
		List<DataSet> dataset = new ArrayList<DataSet>();
		ObjectMapper mapper = new ObjectMapper();
		ObjectNode queryJson = mapper.createObjectNode();
		queryJson.put("name", dataSetName);
		queryJson.put("agencyId", agency);
		queryJson.put("instrument", instrument);
		queryJson.put("physicalVariable", physicalVariable);
		queryJson.put("gridDimension", gridDimension);
		
		if (dataSetEndTime != null) {
			queryJson.put("dataSetEndTime", dataSetEndTime.getTime());
		}
		
		if (dataSetStartTime != null) {
			queryJson.put("dataSetStartTime", dataSetStartTime.getTime());
		}
		JsonNode dataSetNode = APICall.postAPI(DATASET_QUERY, queryJson);
		
		if (dataSetNode == null || dataSetNode.has("error")
				|| !dataSetNode.isArray()) {
			return dataset;
		}

		for (int i = 0; i < dataSetNode.size(); i++) {
			JsonNode json = dataSetNode.path(i);
			DataSet newDataSet = deserializeJsonToDataSet(json);
			dataset.add(newDataSet);
		}
		return dataset;
	}

	private static DataSet deserializeJsonToDataSet(JsonNode json) {
		DataSet newDataSet = new DataSet();
		newDataSet.setId(json.get("id").asText());
		newDataSet.setDataSetName(json.get("name").asText());
		newDataSet.setAgencyId(json.get("agencyId").asText());
		newDataSet.setInstrument(json.get("instrument").get("name").asText());
		newDataSet.setPhysicalVariable(json.get("physicalVariable").asText());
		newDataSet.setCMIP5VarName(json.get("CMIP5VarName").asText());
		newDataSet.setUnits(json.get("units").asText());
		newDataSet.setGridDimension(json.get("gridDimension").asText());
		newDataSet.setSource(json.get("source").asText());
		newDataSet.setStatus(json.get("status").asText());
		newDataSet.setResponsiblePerson(json.get("responsiblePerson").asText());
		newDataSet.setDataSourceName(json.get("dataSourceNameinWebInterface").asText());
		newDataSet.setVariableName(json.get("variableNameInWebInterface").asText());
		newDataSet.setDataSourceInput(json.get("dataSourceInputParameterToCallScienceApplicationCode").asText());
		newDataSet.setVariableNameInput(json.get("variableNameInputParameterToCallScienceApplicationCode").asText());
		String startTime = json.findPath("startTime").asText();
		String endTime = json.findPath("endTime").asText();
		Date tmpTime = null;
		
		try {
			tmpTime = (new SimpleDateFormat("MMM dd, yyyy hh:mm:ss a")).parse(startTime);
			
			if (tmpTime != null) {
				newDataSet.setStartTime(new SimpleDateFormat("YYYYMM").format(tmpTime));
			}
	    } catch (ParseException e){	    
	    }
		
		try {
			tmpTime = (new SimpleDateFormat("MMM dd, yyyy hh:mm:ss a")).parse(endTime);
			
			if (tmpTime != null) {
				newDataSet.setEndTime(new SimpleDateFormat("YYYYMM").format(tmpTime));
			}
	    } catch (ParseException e){	    
	    	
	    }
		return newDataSet;
	}
}
