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

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

public class TimeConvert {

	public static final String timeStamptoDate (String timeStamp) {
		if(timeStamp == ""){
			return "";
		}
		Date date = new Date(Long.parseLong(timeStamp)*1000);
		DateFormat dateFormat = new SimpleDateFormat("MM/dd/yyyy HH:mm");
		String time = dateFormat.format(date);
		return time;
	}
	
	public static final long datetoTimeStamp (String time) throws ParseException{
		if(time == null || time.equals("")){
			return 0;
		}
		SimpleDateFormat dateFormat = new SimpleDateFormat("MM/dd/yyyy HH:mm:ss.SSS");
		String temptime = time + ":00.000";
		Date parsedDate = dateFormat.parse(temptime);
		long timeStamp = parsedDate.getTime();
		return timeStamp;
		
	}
}
