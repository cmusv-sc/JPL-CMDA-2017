// The following is for the code navigation purpose.
//
// ==cmacBase2__
// ==cmacBase3__
// ==cmacBase4__
// ==url_classes
//
// disableButton__(id1)
// disableActionButton__()
// enable_download data button
// disable_pres1__
// enable_pres1__(ID)
// put_data__
// data_block_str__
// change_datan_
// put_var__
// is3D__
// select_var__
// time_range__
// time_range2__
// time_range3__
// monthList__
// fillMonth__
// formMonthStr__
// reset_months__
// no_month_check
// select_all_months__
// select_months__
// getMonthStr__
// select_months_from_str__

// num2scale__
// num2scale2__
// num2scale3__
// scale2num__
// scale2num2__
// scale2num3__

// checkbox2num__
// num2checkbox__
// parse_pres__
// get_querystring__
// showUrl__
// processQueryStr__
// processQueryStr2__ (inputs) {
//
// ==cmacBase2__
// makeUrl__
//makeUrl2_(toServer) # just for conditionalSam
// makeUrla__
// displayUrl_(temp1) {
// getNVar__() {
// hideVar__() {
// processQS__
// processQS2__  # just for conditionalSam
// timeBound__() {
// addDataList_(ID) {
// addVarList_(ID) {
// addPres_(ID)
// enablePres_(ID) { 
// enablePres2_(ID) # just for conditionalSam
// disablePres_(ID) {
// disablePres2_(ID) # just for conditionalSam
// checkTimeL_() {
// checkTimeH_() {
// parseNum_(num1) {
//
// ==cmacBase3__
// makeUrl3__
// makeUrl3a__
// processQS3__
// displayUrl3_ {
//
// ==cmacBase4__
// makeUrl4__
// makeUrl4a__
// processQS4__
// displayUrl4_ {

// ==url_classes
// urlDirect_() {
// urlCheckbox_() {
// urlDash_() {
// urlEscape_() {
// urlRadioTwo_() {
// urlDataUrl_() {
// urlMonths_() {
// urlScale1_() {
// urlScale2_() {
// urlScale3_() {

var naValue = "-999999";

// disableButton__(id1)
function disableButton(id1)
{
  var x=document.getElementById(id1);
  x.disabled=true;
  x.style.background="#999999";
}

function enableButton(id1)
{
  var x=document.getElementById(id1);
  x.disabled=false;
  x.style.background="#4dffa6";
  //x.style.background="#ccff99";
}

// disableActionButton__()
function disableActionButton()
{
  var x=document.getElementById("action1");
  x.disabled=true;
  x.style.background="#999999";
}

function enableActionButton()
{
  var x=document.getElementById("action1");
  x.disabled=false;
  x.style.background="#4dffa6";
  //x.style.background="#ccff99";
}


// disable download data button
function disable_download_button()
{
  var x=document.getElementById("download_data");
  x.disabled=true;
  x.style.background="#999999";
}

// enable_download data button
function enable_download_button()
{
  var x=document.getElementById("download_data");
  x.disabled=false;
  x.style.background="#4dffa6";
}

// disable pressure level box for 2D var
// disable_pres1__
function disable_pres1(ID)
{
  // if isPressure1 is defined, there is no pressure widget 
  try {
    var x;
    x=document.getElementById("pres"+ID);
    x.value = "N/A";
    x.disabled=true;
    var y=document.getElementById("pressureLabel"+ID);
    y.innerHTML = "pressure:";
  }
  catch(err) {}
}

// enable pressure level box for 3D var
// enable_pres1__(ID)
function enable_pres1(ID)
{
  var var_string = $("#var"+ID).val();
  var oceanStr = "";

  try { 
    var rangeStr0 = eval("rangeStr"+ID); 
  } catch(err) { 
    var rangeStr0 = "";
  }

  try {
    var y=document.getElementById("pressureLabel"+ID);
  //alert(y.value);
    y.innerHTML = "atmospheric pressure " + rangeStr0 + "(hPa):";
  } catch(err) {}

  if (varList[var_string][1]==="ocean") {
    oceanStr = "o";
    try {
      y.innerHTML = "ocean pressure " + rangeStr0 + "(dbar):";
    } catch(err) {}
  } 

  // there can be no pressure widget, so there is a error catch here.
  try {
    var pressDf0;
    try { 
      pressDf0 = eval("pressDf"+ID+oceanStr); 
    } catch(err) {
      pressDf0 = "500";
    }


    var x=document.getElementById("pres"+ID);
    x.value = pressDf0;
    x.disabled=false;
  } catch(err) {}
/*  try {
    if ( eval("typeof pressDf"+ID) !== 'undefined') var pressDf0 = eval("pressDf"+ID);
    else var pressDf0 = "500";

    var x=document.getElementById("pres"+ID);
    x.value = pressDf0;
    x.disabled=false;
  } catch(err) {}
*/
}

// put_data__
function put_data(ID){
  var list1=document.getElementById("data"+ID);

  for(var key in dataList) {
    if (key.slice(0,5)==="group") {
      var og = document.createElement("OPTGROUP");
      og.setAttribute('label', dataList[key][0]);
      list1.add(og);

    } else {
      var toAdd = true;

      // whether the dataset has only 2D or only 3D variables
      if   ( (typeof isOnly2d !== 'undefined') 
          || (typeof isOnly3d !== 'undefined') ) {
        var dims = "";
        var varList2 = dataList[key][1];  
        for(var i=0; i<varList2.length; i++)   
          dims += String(varList[ varList2[i] ][2]);

        if (typeof isOnly2d !== 'undefined') 
          if (dims.indexOf('2')==-1) toAdd = false;
        if (typeof isOnly3d !== 'undefined') 
          if (dims.indexOf('3')==-1) toAdd = false;
      }
  
      // add to the option group
      if (toAdd) og.appendChild(new Option(key,key));
    }
  }
}

// change_datan_
function change_datan(numTB, titleStr, lonDf, latDf, timeDf){
  var nVar=Number( document.getElementById("nVar").value );

  if (titleStr == undefined) titleStr = "Source Variable";
  if (lonDf == undefined) lonDf = [];
  if (latDf == undefined) latDf = [];
  if (timeDf == undefined) timeDf = [];

  for (var i=0; i<nVar; i++) {
    var str1 = data_block_str(String(i+2), numTB, titleStr+" "+String(i+1), "", 500, lonDf, latDf, timeDf);
    //alert(str1);
    document.getElementById("datan"+(i+1)).innerHTML = str1;
    put_data(i+2);
    put_var(i+2);
    select_var(i+2);
    if (timeDf.length > 2) {
      fillMonth(i+2);
    }
  }
  for (var i=nVar; i<10; i++) {
    document.getElementById("datan"+(i+1)).innerHTML = "";
  }
}

// data_block_str__
function data_block_str(ID, numTB, dataTitle, isRange, pressDf, lonDf, latDf, timeDf) {
var temp1= '';
if (lonDf == undefined) lonDf = [];
if (latDf == undefined) latDf = [];
temp1 += '<div class="row ">\n'
temp1 += '<div class="col-sm-12 center1 subtitle1">\n';
temp1 += dataTitle + '\n';
temp1 += '</div>\n';
temp1 += '</div> <!-- row --> \n';

temp1 += '<div class="row">\n';
temp1 += ' <div class="col-sm-4 right1">\n';
temp1 += '   source:' + '\n';
temp1 += '  </div> <!-- col-sm-6 -->\n';
temp1 += '  <div class="col-sm-8 left1">\n';
temp1 += '    <select name="data' + ID + '", id="data' + ID;
temp1 += '" onchange="put_var(' + ID + '); select_var(' + ID + ');time_range' + numTB + '()"></select>\n';
temp1 += '  </div> <!-- col-sm-6 level2-->\n';
temp1 += '</div> <!-- row -->\n';

temp1 += '<div class="row">\n';
temp1 += '  <div class="col-sm-4 right1">\n';
temp1 += '    variable name:\n';
temp1 += '  </div> <!-- col-sm-6 level2-->\n';
temp1 += '  <div class="col-sm-8 left1">\n';
temp1 += '    <select name="var' + ID +'", id="var' + ID;
temp1 += '" onchange="select_var(' + ID + '); select_var(' + ID + '); time_range' + numTB + '()"> </select>\n';
temp1 += '  </div> <!-- col-sm-6 level2-->\n';
temp1 += '</div> <!-- row -->\n';

if (lonDf.length == 2) {
  temp1 +=  '<div class="row">\n'
  temp1 +=  '  <div class="col-sm-4 right1">\n'
  temp1 +=  '    start lon (deg):\n'
  temp1 +=  '  </div>\n'
  temp1 +=  '  <div class="col-sm-2 left1">\n'
  temp1 +=  '  <input id="lon0_' + ID + '", value="'  + lonDf[0] + '" size=7>\n'
  temp1 +=  '  </div>\n'
  temp1 +=  '  <div class="col-sm-4 right1">\n'
  temp1 +=  '    end lon (deg):\n'
  temp1 +=  '  </div>\n'
  temp1 +=  '  <div class="col-sm-2 left1">\n'
  temp1 +=  '    <input id="lon1_' + ID + '",  value="' + lonDf[1] + '" size=7>\n'
  temp1 +=  '  </div>\n'
  temp1 +=  '</div> <!-- row -->\n'
}

if (latDf.length == 2) {
  temp1 +=  '<div class="row">\n'
  temp1 +=  '  <div class="col-sm-4 right1">\n'
  temp1 +=  '    start lat (deg):\n'
  temp1 +=  '  </div>\n'
  temp1 +=  '  <div class="col-sm-2 left1">\n'
  temp1 +=  '  <input id="lat0_' + ID + '", value="' + latDf[0] + '" size=7>\n'
  temp1 +=  '  </div>\n'
  temp1 +=  '  <div class="col-sm-4 right1">\n'
  temp1 +=  '    end lat (deg):\n'
  temp1 +=  '  </div>\n'
  temp1 +=  '  <div class="col-sm-2 left1">\n'
  temp1 +=  '    <input id="lat1_' + ID + '",  value="' + latDf[1] + '" size=7>\n'
  temp1 +=  '  </div>\n'
  temp1 +=  '</div> <!-- row -->\n'
}

if (timeDf.length >= 2) {
  if (timeDf.length > 2) {
    temp1 += '<div class="row">\n'
    temp1 += '  <div class="col-sm-4 right1">\n'
    temp1 += '    <div id="monthSelect0_' + ID + '"></div>\n'
    temp1 += '  </div>\n'
    temp1 += '  <div class="col-sm-8 left1">\n'
    temp1 += '    <div id="monthSelect_' + ID + '"></div>\n'
    temp1 += '  </div>\n'
    temp1 += '</div> <!-- row --> \n'
  }
  temp1 +=  '<div class="row">\n'
  temp1 +=  '  <div class="col-sm-4 right1">\n'
  temp1 +=  '    <div id=startYear>start year-month:</div>\n'
  temp1 +=  '  </div>\n'
  temp1 +=  '  <div class="col-sm-2 left1">\n'
  temp1 +=  '  <input id="t0_' + ID + '", value="' + timeDf[0] + '" alt="start" size=7>\n'
  temp1 +=  '<div class="row">\n';
  temp1 +=  '  <div class="col-sm-4 right1">\n';
  temp1 +=  '    <div id=startYear>start year-month:</div>\n';
  temp1 +=  '  </div>\n';
  temp1 +=  '  <div class="col-sm-2 left1">\n';
  temp1 +=  '  <input id="t0_' + ID + '", value="' + Math.floor(timeDf[0]/100) + '-' + Math.floor((timeDf[0] % 100)/10) + (timeDf[0] % 10) + '" alt="start" size=7>\n'
  temp1 +=  '  </div>\n'
  temp1 +=  '  <div class="col-sm-4 right1">\n'
  temp1 +=  '    <div id=endYear>end year-month:</div>\n'
  temp1 +=  '  </div>\n'
  temp1 +=  '  <div class="col-sm-2 left1">\n'
  temp1 +=  '    <input id="t1_' + ID + '",  value="' + timeDf[1] + '" alt="end" size=7>\n'
  temp1 +=  '  <input id="t1_' + ID + '", value="' + Math.floor(timeDf[1]/100) + '-' + Math.floor((timeDf[1] % 100)/10) + (timeDf[1] % 10) + '" alt="start" size=7>\n'
  temp1 +=  '  </div>\n'
  temp1 +=  '</div> <!-- row -->\n'
}

temp1 += '<div class="row">\n';
temp1 += '  <div class="col-sm-4 right1" id="pressureLabel' + ID + '">\n';
//temp1 += '    pressure ' + isRange + '(atmosphere hPa) <br> or (ocean dbar):\n';
temp1 += '    pressure ' + isRange +':\n';
temp1 += '  </div> <!-- col-sm-6 level2-->\n';
temp1 += '  <div class="col-sm-8 left1">\n';
temp1 += '    <input id="pres' + ID + '" value="' + pressDf + '" alt="pressure"/>\n';
temp1 += '  </div> <!-- col-sm-6 level2-->\n';
temp1 += '</div> <!-- row -->\n';
// alert(temp1);
return temp1;
}

// put_var__
function put_var(ID) {
  var list1=document.getElementById("var"+ID);
  for (var i=list1.length-1; i>=0; i--) {
  list1.remove(i);
  }

  data_string =  document.getElementById("data"+ID).value;
  //alert("put_var: " + ID + " " + data_string);
  var varList2 = dataList[data_string][1];  

  if (typeof isOnly2d !== 'undefined') {
    // list only 2D variables
    for (var i=0; i<varList2.length; i++) {
      var k = varList2[i];
      if (varList[k][2]==2) list1.add(new Option(varList[k][0],k));
    }

  } else if (typeof isOnly3d !== 'undefined') {
    // list only 3D variables
    for (var i=0; i<varList2.length; i++) {
      var k = varList2[i];
      if (varList[k][2]==3) list1.add(new Option(varList[k][0],k));
    }

  } else {
    // list all 2D/3D variables
    for (var i=0; i<varList2.length; i++) {
      var k = varList2[i];
      list1.add(new Option(varList[k][0],k));
    }
  }

  var nVar = list1.options.length;
  if (nVar==0) {
    alert(data_string + " has no suitable variable.");
    document.getElementById("data"+ID).options[0].selected = true; 
    put_var(ID);
  }
}

// is3D__
function is3D(ID)
{
  var var_string = $("#var"+ID).val();
  return varList[var_string][2]==3;
}

// select_var__
function select_var(ID)
{
  // if there isOnly2d is defined, there is no pressure widget.
  try {
    //var var_string = $("#var"+ID).val();
    //alert(is3D(ID));
    if (is3D(ID)) {
      enable_pres1(ID);
    } else {
      disable_pres1(ID);
    }
  }
  catch(err) {}
}


// time_range__
// this is identical to time_range1()
function time_range() {
  var var_string1 = $("#var"+1).val();
  var data_string1 = $("#data"+1).val();

  var sTime = dataList[data_string1][2][var_string1][0].toString();
  var eTime = dataList[data_string1][2][var_string1][1].toString();

  $("#startYear").html("start year-month: (earliest:" + sTime.slice(0,4) + "-" + sTime.slice(4,6) + ")");
  $("#endYear").html("end year-month: (latest:" + eTime.slice(0,4) + "-" + eTime.slice(4,6) + ")");
}

function time_range1() {
  var var_string1 = $("#var"+1).val();
  var data_string1 = $("#data"+1).val();

  var sTime = dataList[data_string1][2][var_string1][0].toString();
  var eTime = dataList[data_string1][2][var_string1][1].toString();

  $("#startYear").html("start year-month: (earliest:" + sTime.slice(0,4) + "-" + sTime.slice(4,6) + ")");
  $("#endYear").html("end year-month: (latest:" + eTime.slice(0,4) + "-" + eTime.slice(4,6) + ")");
}

// time_range2__
function time_range2() {
  var var_string1 = $("#var"+1).val();
  var var_string2 = $("#var"+2).val();
  var data_string1 = $("#data"+1).val();
  var data_string2 = $("#data"+2).val();
  //alert(data_string1);
  //alert(data_string2);
  

  var sTime = Math.max( Number(dataList[data_string1][2][var_string1][0]),
                        Number(dataList[data_string2][2][var_string2][0]) ).toString();
  var eTime = Math.min( Number(dataList[data_string1][2][var_string1][1]),
                        Number(dataList[data_string2][2][var_string2][1]) ).toString();

  //sTime = sTime.toString();
  //eTime = eTime.toString();

  $("#startYear").html("start year-month: (earliest:" + sTime.slice(0,4) + "-" + sTime.slice(4,6) + ")");
  $("#endYear").html("end year-month: (latest:" + eTime.slice(0,4) + "-" + eTime.slice(4,6) + ")");
}

// time_range3__
function time_range3() {
  var var_string1 = $("#var"+1).val();
  var var_string2 = $("#var"+2).val();
  var var_string3 = $("#var"+3).val();
  var data_string1 = $("#data"+1).val();
  var data_string2 = $("#data"+2).val();
  var data_string3 = $("#data"+3).val();

  var sTime = Math.max( 
        Number(dataList[data_string1][2][var_string1][0]),
        Number(dataList[data_string2][2][var_string2][0]),
        Number(dataList[data_string3][2][var_string3][0]) 
        ).toString();
  var eTime = Math.min(
        Number(dataList[data_string1][2][var_string1][1]),
        Number(dataList[data_string2][2][var_string2][1]),
        Number(dataList[data_string3][2][var_string3][1]) 
        ).toString();

  $("#startYear").html("start year-month: (earliest:" + sTime.slice(0,4) + "-" + sTime.slice(4,6) + ")");
  $("#endYear").html("end year-month: (latest:" + eTime.slice(0,4) + "-" + eTime.slice(4,6) + ")");
}

// monthList__
var monthList = [
"Jan",
"Feb",
"Mar",
"Apr",
"May",
"Jun",
"Jul",
"Aug",
"Sep",
"Oct",
"Nov",
"Dec",
];

var monthList2 = {
"Jan":"1",
"Feb":"2",
"Mar":"3",
"Apr":"4",
"May":"5",
"Jun":"6",
"Jul":"7",
"Aug":"8",
"Sep":"9",
"Oct":"10",
"Nov":"11",
"Dec":"12",
};

// fillMonth__
// better to write it out.
function fillMonth(varIdx) { 
  var id_ext = '';
  if (varIdx !== undefined)  {
    id_ext = "_" + varIdx;
  }
  var temp1 = 'select months: <select name="months" id="months' + id_ext + '"';
  temp1 += ' onchange="select_months(' + varIdx + ')">';
  temp1 += '<option id="all">select all</option><option id="none">select none</option>';
  temp1 += '<option id="summer' + id_ext + '">Summer:Jun-Jul-Aug</option>';
  temp1 += '<option id="autumn' + id_ext + '">Autumn:Sep-Oct-Nov</option>';
  temp1 += '<option id="winter' + id_ext + '">Winter:Dec-Jan-Feb</option>';
  temp1 += '<option id="spring' + id_ext + '">Spring:Mar-Apr-May</option> </select>';

  $("#monthSelect0" + id_ext).html(temp1); 

  temp1 = '<form role="form">'; 
  for (var i=0; i<monthList.length; i++) {
    temp1 +=
        '<label"><input type="checkbox" id="' + monthList[i] + id_ext + '" value="' + monthList[i] + '" checked/></label>' 
          +  monthList[i] + " ";
  }
  temp1 += '</form>';
  $("#monthSelect" + id_ext).html(temp1); 
}

// formMonthStr__
// loop through 12 month check boxes and grab the status
function formMonthStr(varIdx) { 
  var id_ext = '';
  if (varIdx !== undefined) {
    id_ext = "_" + varIdx;
  }

  // get months checked by client
  var month_str = "";

  var firstMonth = true;
  for (var i = 0; i < monthList.length; ++i)
  {
    var mm = document.getElementById(monthList[i] + id_ext);
    if (mm.checked == true) {
      if (!firstMonth) {
        month_str += ",";
      }
      month_str += monthList2[monthList[i]];
      firstMonth = false;
    }
  }
  return month_str;
}

// unselect all months in the checkboxes
// reset_months__
function reset_months(varIdx)
{
  var id_ext = '';
  if (varIdx !== undefined)  {
    id_ext = "_" + varIdx;
  }
  for (var i=0; i<monthList.length; i++) {
    document.getElementById(monthList[i] + id_ext).checked = false;
  }
}

// see if no month is selected
// no_month_check
function no_month_check(varIdx)
{
  var nonChecked = true;
  var id_ext = '';
  if (varIdx !== undefined)  {
    id_ext = "_" + varIdx;
  }
  for (var i=0; i<monthList.length; i++) {
    if (document.getElementById(monthList[i] + id_ext).checked == true) {
      nonChecked = false;
    }
  }
  return nonChecked;
}

// select all months in the checkboxes
// select_all_months__
function select_all_months(varIdx)
{
  var id_ext = '';
  if (varIdx !== undefined)  {
    id_ext = "_" + varIdx;
  }
  for (var i=0; i<monthList.length; i++) {
    document.getElementById(monthList[i]+id_ext).checked = true;
  }
}

// select checkboxes based on "months" dropdown
// select_months__
function select_months(varIdx)
{
  var id_ext = '';
  if (varIdx !== undefined)  {
    id_ext = "_" + varIdx;
  }
  var s1=document.getElementById("months"+id_ext);
  // alert(s1.selectedIndex);
  // alert(s1.options[s1.selectedIndex].value);

  // disable the download button because of this change
  disable_download_button();

  // "select none"
  if (s1.selectedIndex == 1) {
    reset_months(varIdx);
  }
  // "select all"
  if (s1.selectedIndex == 0) {
    select_all_months(varIdx);
  }
  // "summer"
  if (s1.selectedIndex == 2) {
    reset_months(varIdx);
    document.getElementById('Jun'+id_ext).checked = true;
    document.getElementById('Jul'+id_ext).checked = true;
    document.getElementById('Aug'+id_ext).checked = true;
  }
  // "autumn"
  if (s1.selectedIndex == 3) {
    reset_months(varIdx);
    document.getElementById('Sep'+id_ext).checked = true;
    document.getElementById('Oct'+id_ext).checked = true;
    document.getElementById('Nov'+id_ext).checked = true;
  }
  // "winter"
  if (s1.selectedIndex == 4) {
    reset_months(varIdx);
    document.getElementById('Dec'+id_ext).checked = true;
    document.getElementById('Jan'+id_ext).checked = true;
    document.getElementById('Feb'+id_ext).checked = true;
  }
  // "spring"
  if (s1.selectedIndex == 5) {
    reset_months(varIdx);
    document.getElementById('Mar'+id_ext).checked = true;
    document.getElementById('Apr'+id_ext).checked = true;
    document.getElementById('May'+id_ext).checked = true;
  }
}

// select_months_from_str__
function select_months_from_str(str1, varIdx)
{
  var id_ext = '';
  if (varIdx !== undefined)  {
    id_ext = "_" + varIdx;
  }
  reset_months();
  // even for an empty str1, temp2.length=1
  var temp2 = str1.split(",");
  var ii;
  for (var i=0; i<temp2.length; i++) {
    try {
      ii = Number(temp2[i]);
      document.getElementById(monthList[ii-1] + id_ext).checked = true;
    } catch(err) {}
  }
}

// num2scale__
// for id=scale
function num2scale(ii)
{
  if (displayOpt=="1") {
    // radioLog =true -> 2
    if (ii==0) { 
      document.getElementById("radioLin").checked = true;
    } else if ( ii==2 ) {
      document.getElementById("radioLog").checked = true;
    }

  } else if (displayOpt=="2") {
    // radioLog2=true -> 1
    // radioLog =true -> 2
    if (ii==0) { 
      document.getElementById("radioLin").checked = true;
      document.getElementById("radioLin2").checked = true;
    } else if ( ii==1 ) {
      document.getElementById("radioLin").checked = true;
      document.getElementById("radioLog2").checked = true;
    } else if ( ii==2 ) {
      document.getElementById("radioLog").checked = true;
      document.getElementById("radioLin2").checked = true;
    } else if ( ii==3 ) {
      document.getElementById("radioLog").checked = true;
      document.getElementById("radioLog2").checked = true;
    }
  }
}

function num2scale1(ii)
{
  if (ii==0) { 
    document.getElementById("radioLin").checked = true;
  } else if ( ii==2 ) {
    document.getElementById("radioLog").checked = true;
  }
}

// num2scale3__
// for id=scale3
function num2scale3(ii)
{
  // radioLog =true -> 1
  // radioLog2=true -> 2
  // radioLog3=true -> 4
  if (ii==0) { 
    document.getElementById("radioLin").checked = true;
    document.getElementById("radioLin2").checked = true;
    document.getElementById("radioLin3").checked = true;
  } else if ( ii==1 ) {
    document.getElementById("radioLog").checked = true;
    document.getElementById("radioLin2").checked = true;
    document.getElementById("radioLin3").checked = true;
  } else if ( ii==2 ) {
    document.getElementById("radioLin").checked = true;
    document.getElementById("radioLog2").checked = true;
    document.getElementById("radioLin3").checked = true;
  } else if ( ii==3 ) {
    document.getElementById("radioLog").checked = true;
    document.getElementById("radioLog2").checked = true;
    document.getElementById("radioLin3").checked = true;
  } else if ( ii==4 ) {
    document.getElementById("radioLin").checked = true;
    document.getElementById("radioLin2").checked = true;
    document.getElementById("radioLog3").checked = true;
  } else if ( ii==5 ) {
    document.getElementById("radioLog").checked = true;
    document.getElementById("radioLin2").checked = true;
    document.getElementById("radioLog3").checked = true;
  } else if ( ii==6 ) {
    document.getElementById("radioLin").checked = true;
    document.getElementById("radioLog2").checked = true;
    document.getElementById("radioLog3").checked = true;
  } else if ( ii==7 ) {
    document.getElementById("radioLog").checked = true;
    document.getElementById("radioLog2").checked = true;
    document.getElementById("radioLog3").checked = true;
  }
}

// num2scale2__
// for id=scale2
function num2scale2(ii)
{
  // radioLog =true -> 4
  // radioLog2=true -> 2
  if (ii==0) { 
    document.getElementById("radioLin").checked = true;
    document.getElementById("radioLin2").checked = true;
  } else if ( ii==2 ) {
    document.getElementById("radioLin").checked = true;
    document.getElementById("radioLog2").checked = true;
  } else if ( ii==4 ) {
    document.getElementById("radioLog").checked = true;
    document.getElementById("radioLin2").checked = true;
  } else if ( ii==6 ) {
    document.getElementById("radioLog").checked = true;
    document.getElementById("radioLog2").checked = true;
  }
}

// scale2num__
function scale2num() {
  var out1, t1, t2; 

  if (displayOpt=="1") {
    if ( document.getElementById("radioLin").checked ) {
      t1 = 0;
    } else { 
      t1 = 2;
    }
    return t1;

  } else if (displayOpt=="2") {
    if ( document.getElementById("radioLin").checked ) {
      t1 = 0;
    } else { 
      t1 = 2;
    }

    if ( document.getElementById("radioLin2").checked ) {
      t2 = 0;
    } else { 
      t2 = 1;
    }

    return  t1 + t2;
  }
}

// scale2num1__
function scale2num1() {
  var out1, t1, t2; 

  if ( document.getElementById("radioLin").checked ) {
    t1 = 0;
  } else { 
    t1 = 2;
  }
  return t1;
}

// scale2num2__
function scale2num2() {
  var out1, t1, t2; 

  if ( document.getElementById("radioLin").checked ) {
    t1 = 0;
  } else { 
    t1 = 2;
  }

  if ( document.getElementById("radioLin2").checked ) {
    t2 = 0;
  } else { 
    t2 = 4;
  }

  return  t1 + t2;
}

// scale2num3__
function scale2num3() {
  var out1, t1, t2, t3; 

  if ( document.getElementById("radioLin").checked ) {
    t1 = 0;
  } else { 
    t1 = 1;
  }

  if ( document.getElementById("radioLin2").checked ) {
    t2 = 0;
  } else { 
    t2 = 2;
  }

  if ( document.getElementById("radioLin3").checked ) {
    t3 = 0;
  } else { 
    t3 = 4;
  }

  return  t1 + t2 + t3;
}

// checkbox2num__(id1) {
function checkbox2num(id1) {
  if ( document.getElementById(id1).checked ) {
    return 1;
  } else {
    return 0;
  }
}

// num2checkbox__
function num2checkbox(id1, num1) {
  if ( num1==1 ) {
    document.getElementById(id1).checked = true;
  } else {
    document.getElementById(id1).checked = false;
  }
}

// getMonthStr__
function getMonthStr() {
        // get months checked by client
        var month_str = "";
        for (var i=0; i<monthList.length; i++) {
          var mm = document.getElementById(monthList[i]);
          if (mm.checked == true) {
            month_str += ","+(i+1);
          }
        }
        month_str = month_str.substr(1);
        return month_str;
}

// parse_pres__
function parse_pres(pres10) {
  var pres1 = "";

  if (pres10=="") {pres1 = naValue; }
  else {
    if (!(isNaN(Number(pres10)))) { 
      pres1 = pres10; 
    } else {
      var checkNan = 0;
      var pres2 = [];
      var temp1=pres10.split(",");
      //for (var i in temp1) {
      for (var i=0; i<temp1.length; i++) {
        if (isNaN(Number(temp1[i]))) {
          checkNan = 1; 
        } else {
          pres2.push(Number(temp1[i]));
        }
      }
      if (pres2.length>0) { pres1 = pres2.join(); }
      else { pres1 = naValue; }
    }
  }
  return pres1;
}

// get_querystring__
function get_querystring() {
  var queries = {};
  //var temp1 = document.location.search.substr(1).split('&');
  //alert(temp1.length);
  $.each(document.location.search.substr(1).split('&'),function(c,q){
    var i = q.split('=');
    //alert(i.length);
    try { 
    //if (i.lengh==2) { 
      queries[i[0].toString()] = i[1].toString();
    //}
    } catch(err) {}
  });
  return queries;
}


// showUrl__
function showUrl(inputs) {
  var vq, v2, key0, key1;
  try {
    var temp1 = "";
    //for (var i=0; i<inputs.length; i++) {
    for (key0 in inputs) {
      if (!inputs.hasOwnProperty(key0)) { continue; }
      //if ( key0 == "Image" || key0 == "data_url" ) { continue; }

      key1 = inputs[key0];

      try {
        if ( key0 == "Image" ) {
          try {
            vq = document.querySelectorAll('#Image img')[0].src;
          } catch(err) {
            continue;
          }

        } else {
          vq = $("#"+key1).val();
        }

        if ( key0.slice(0,5) == "model" ) {
          vq = vq.replace("/", "_");

        } else if ( key0 == "startT" || key0 == "endT" ) {
          vq = vq.replace("-", "");

        } else if ( key0 == "purpose" ) {
          if ( vq=="" ) {
            continue;
          }
          vq = escape(vq);

        } else if ( key0 == "data_url" ) {
          vq = escape(vq);
          var temp2 = escape("Data URL");
          if ( vq.indexOf(temp2)>=0 ) {
            continue;
          }

        } else if ( key0 == "months" ) {
          vq = getMonthStr();

        } else if ( key1 == "scale" ) {
          vq = scale2num();

        } else if ( key1 == "scale2" ) {
          vq = scale2num2();

        } else if ( key1 == "anomaly" ) {
          vq = checkbox2num(key1);

        }
/*
        if ( key0.slice(0,4) == "pres" ) {
          if ( Number(v1q) == NaN ) {
            vq = "-999999";
          }
        }
*/
        temp1 += key0 + "=" + vq + "&";
      } catch(err) {}
    }
    temp1 = temp1.slice(0,-1);
  } catch(err) { 
    var temp1 = document.location.search.substr(1);
  }

  document.getElementById("actionUrl").innerHTML = document.location.href.split('?')[0] + "?" + temp1;
}

// processQueryStr__
// it is a reverse process of showUrl()
function processQueryStr(inputs) {
  queries = get_querystring();

  var key0, key1, vq;

  for (key0 in queries) {
    if (!queries.hasOwnProperty(key0)) { continue; }
    if (!inputs.hasOwnProperty(key0)) { continue; }
    key1 = inputs[key0];
    vq = queries[key0];
    vq = vq.trim();

    if ( key0.slice(0,5) == "model" ) {
      vq = vq.replace("_", "/");
    }

    if ( key0 == "startT" || key0 == "endT" ) {
      vq = vq.slice(0,4) + "-" + vq.slice(4,6);
    }

    if ( key0 == "purpose" ) {
      vq = unescape(vq);
    }

    if ( key0 == "data_url" ) {
      vq = unescape(vq);
    }


    //try {
      if ( key1 == "Image" ) {
        //$("#"+key1).html( "<img id=imgSrc src='" + vq + "' width='820'/>" );
        $("#"+key1).html( "<img id=imgSrc src='" + vq + "'>" );

      } else if ( key1 == "data_url" ) {
        $("#"+key1).val( vq );
        enable_download_button();

      } else if ( key1 == "months" ) {
        select_months_from_str(vq);

      } else if ( key1 == "scale" ) {
        num2scale(Number(vq));

      } else if ( key1 == "scale2" ) {
        num2scale2(Number(vq));

      } else if ( key1 == "anomaly" ) {
        num2checkbox(key1, Number(vq));

      } else {
        $("#"+key1).val(vq);
        $("#"+key1).change();
      }
    //} catch(err) {}
  }
}

// for twoDimSlice3D
// processQueryStr2__ (inputs) {
function processQueryStr2(inputs) {
  queries = get_querystring();

  var key0, key1, vq;

  for (key0 in queries) {
    if (!queries.hasOwnProperty(key0)) { continue; }
    if (!inputs.hasOwnProperty(key0)) { continue; }
    key1 = inputs[key0];
    vq = queries[key0];
    vq = vq.trim();

    if ( key0.slice(0,5) == "pres1" ) {
      if (queries['var1'] == 'ot' || queries['var1'] == 'os')
        vq = (Number(vq) / 10000).toString();
      else
        vq = (Number(vq) / 100).toString();
    }

    if ( key0.slice(0,5) == "model" ) {
      vq = vq.replace("_", "/");
    }

    if ( key0 == "startT" || key0 == "endT" ) {
      vq = vq.slice(0,4) + "-" + vq.slice(4,6);
    }

    if ( key0 == "purpose" ) {
      vq = unescape(vq);
    }

    //try {
      if ( key1 == "Image" ) {
        $("#"+key1).html( "<img src='" + vq + "' width='820'/>" );

      } else if ( key1 == "data_url" ) {
        $("#"+key1).val( vq );
        enable_download_button();

      } else if ( key1 == "months" ) {
        select_months_from_str(vq);

      } else if ( key1 == "scale" ) {
        num2scale(Number(vq));

      } else if ( key1 == "scale2" ) {
        num2scale2(Number(vq));

      } else {
        $("#"+key1).val(vq);
        $("#"+key1).change();
      }
    //} catch(err) {}
  }
}

// makeUrl__
// the following not working with chrome:
//function makeUrl(toServer=false) {

function makeUrl(toServer) {
  toServer = typeof toServer !== 'undefined' ? toServer:false;

  var vq, key0, key1, nVar;
  var temp1 = "";

  nVar = getNVar();
  for(var i=0; i<nVar; i++) {
    key0 = "model"+(i+1);
    key1 = "data"+(i+1);
    vq = $("#"+key1).val();
    vq = vq.replace("/", "_");
    if ( toServer ) {
      vq = vq.toLowerCase();
    }
    temp1 += key0 + "=" + vq + "&";

    key0 = "var"+(i+1);
    key1 = key0;
    vq = $("#"+key1).val();
    temp1 += key0 + "=" + vq + "&";

    key0 = "pres"+(i+1);
    key1 = key0;
    vq = $("#"+key1).val();
    vq = parse_pres(vq);
    temp1 += key0 + "=" + vq + "&";
  }

  for (key0 in inputs) {
    if (!inputs.hasOwnProperty(key0)) { continue; }

    key1 = inputs[key0];

    try {
      vq = $("#"+key1).val();
    } catch(err) {
      vq = "";
    }

    // the alert here generates an error:
    // alert(key0+"  "+vq);

    if ( key1 == "startT" || key1 == "endT" ) {
      vq = vq.replace("-", "");

    } else if ( key1 == "purpose" ) {
      // not to do "purpose" if it is empty
      //if ( vq=="" && !toServer ) {
      //  continue;
      //}
      vq = escape(vq);

    //} else if ( key0 == "nVar" ) {
    //  vq = nVarI + nVarP;
    //  }

    } else if ( key1 == "months" ) {
      vq = getMonthStr();

    } else if ( key1 == "scale" ) {
      vq = scale2num();

    } else if ( key1 == "scale2" ) {
      vq = scale2num2();

    } else if ( key1 == "scale3" ) {
      vq = scale2num3();

    } else if ( key1 == "anomaly" ) {
      vq = checkbox2num(key1);

    }
/*
      if ( key0.slice(0,4) == "pres" ) {
        if ( Number(v1q) == NaN ) {
          vq = "-999999";
        }
      }
*/
    temp1 += key0 + "=" + vq + "&";
  }

  temp1 = temp1.slice(0,-1);

  if (toServer) { return temp1; }

  else {
    temp1 = document.location.href.split('?')[0] + "?" + temp1;
    return temp1;
  }
}

//makeUrl2_(toServer) {
function makeUrl2(toServer) {
  toServer = typeof toServer !== 'undefined' ? toServer:false;

  var vq, key0, key1, nVar;
  var temp1 = "";

  nVar = getNVar();
  for(var i=0; i<nVar; i++) {
    key0 = "model"+(i+1);
    key1 = "data"+(i+1);
    vq = $("#"+key1).val();
    vq = vq.replace("/", "_");
    if ( toServer ) {
      vq = vq.toLowerCase();
    }
    temp1 += key0 + "=" + vq + "&";

    key0 = "var"+(i+1);
    key1 = key0;
    vq = $("#"+key1).val();
    temp1 += key0 + "=" + vq + "&";

    key0 = "pres"+(i+1);
    key1 = key0;
    vq = $("#"+key1).val();
    vq = parse_pres(vq);
    temp1 += key0 + "=" + vq + "&";

    if ( dList[i]["isPressureRange"] ) {
      key0 = key0 + "a";
      key1 = key0;
      vq = $("#"+key1).val();
      vq = parse_pres(vq);
      temp1 += key0 + "=" + vq + "&";
    }
  }

  for (key0 in inputs) {
    if (!inputs.hasOwnProperty(key0)) { continue; }

    key1 = inputs[key0];

    try {
      vq = $("#"+key1).val();
    } catch(err) {
      vq = "";
    }

    // the alert here generates an error:
    // alert(key0+"  "+vq);

    if ( key1 == "startT" || key1 == "endT" ) {
      vq = vq.replace("-", "");

    } else if ( key1 == "purpose" ) {
      // not to do "purpose" if it is empty
      //if ( vq=="" && !toServer ) {
      //  continue;
      //}
      vq = escape(vq);

    //} else if ( key0 == "nVar" ) {
    //  vq = nVarI + nVarP;
    //  }

    } else if ( key1 == "months" ) {
      vq = getMonthStr();

    } else if ( key1 == "scale" ) {
      vq = scale2num();

    } else if ( key1 == "scale2" ) {
      vq = scale2num2();

    } else if ( key1 == "scale3" ) {
      vq = scale2num3();

    } else if ( key1 == "anomaly" ) {
      vq = checkbox2num(key1);

    } else if ( 
               key1 == "binMin2" 
            || key1 == "binMax2" 
            || key1 == "binN2" 
            || key1 == "binMin3" 
            || key1 == "binMax3" 
            || key1 == "binN3" 
              
               ) {
      vq = parseNum(vq);
    }

/*
      if ( key0.slice(0,4) == "pres" ) {
        if ( Number(v1q) == NaN ) {
          vq = "-999999";
        }
      }
*/
    temp1 += key0 + "=" + vq + "&";
  }

  temp1 = temp1.slice(0,-1);

  if (toServer) { return temp1; }

  else {
    temp1 = document.location.href.split('?')[0] + "?" + temp1;
    return temp1;
  }
}
// makeUrla__
function makeUrla() {
  var vq, key0, key1; 
  var temp1 = makeUrl();
  //alert(temp1);
  try {
    vq = document.querySelectorAll('#Image img')[0].src;
  } catch(err) { }

    //var temp2 = typeof vq;
    //alert(temp2);
    //alert(vq);
  if (typeof vq !== 'undefined') {
    key0 = "Image";
    //alert("&" + key0 + "=" + vq);
    temp1 += "&" + key0 + "=" + vq;
  }

  //try {
    key0 = "data_url";
    key1 = key0;
    vq = $("#"+key1).val();
    vq = escape(vq);
    var temp2 = escape("Data URL");
    if ( vq.indexOf(temp2)<0 ) {
      temp1 += "&" + key0 + "=" + vq;
    }
  //} catch(err) { }

  return temp1;
}

// displayUrl_ {
function displayUrl() {
  var temp1 = makeUrl();
  //alert(temp1);
  //document.getElementById("actionUrl").innerHTML = temp1;
  document.getElementById("actionUrl").value = temp1;
}

function displayUrla() {
  var temp1 = makeUrla();
  document.getElementById("actionUrl").value = temp1;
}

// getNVar__() {
function getNVar() {
 if ( isNVar ) {
   return ( Number( $("#nVar").val() ) + nVarP );
 } else {
   return nVar0;
 }
}

// hideVar__() {
function hideVar() {
  var nVarI = Number( $("#nVar").val() );
  //alert( nVar + 1);
  //alert( nVar0 + 1);
  //alert( nVarP + 1);
  for(var i=0; i<nVar0; i++) {
    if (i<nVarI + nVarP ) {
      $("#dataBlock"+(i+1)).show();
    } else {
      $("#dataBlock"+(i+1)).hide();
    }
  }
}

function fetchQValue(queries, key0) {
  var vq;
  if (!queries.hasOwnProperty(key0)) { 
    return false; 

  } else {
    return queries[key0];
  }
}

// processQS__
function processQS() {
  queries = get_querystring();

  if (queries.length<1) {return;}

  var key0, key1, vq, nVar;

  if ( queries.hasOwnProperty("nVar") 
     && inputs.hasOwnProperty("nVar") )  {
    nVar = Number(queries["nVar"]) + nVarP;
  } else {
    nVar = nVar0;
  }

  for(var i=0; i<nVar; i++) {
    key0 = "model"+(i+1);
    key1 = "data"+(i+1);
    vq = fetchQValue(queries, key0);
    if (vq !==false) {
      vq = vq.replace("_", "/");
      $("#"+key1).val(vq);
      $("#"+key1).change();
    }
  
    key0 = "var"+(i+1);
    key1 = key0;
    vq = fetchQValue(queries, key0);
    if (vq !==false) {
      $("#"+key1).val(vq);
      $("#"+key1).change();
    }

    key0 = "pres"+(i+1);
    key1 = key0;
    vq = fetchQValue(queries, key0);
    if (vq !==false) {
      if (vq=="-999999") {
        vq = "N/A";
      }
      $("#"+key1).val(vq);
      $("#"+key1).change();
    }
  }

  for (key0 in queries) {
    if ( key0.slice(0,5) == "model" ) { continue; }
    if ( key0.slice(0,3) == "var" ) { continue; }
    if ( key0.slice(0,4) == "pres" ) { continue; }

    vq = fetchQValue(queries, key0);
    if (vq ===false) { continue; }

    vq = vq.trim();
   
    // Image and data_url have no key1
    if ( key0 == "Image" || key0 == "data_url" ) {
      key1 = key0;
    } else {
      key1 = inputs[key0];
    }
    //vq = queries[key0];

    if ( key1 == "startT" || key1 == "endT" ) {
      vq = vq.slice(0,4) + "-" + vq.slice(4,6);
    }

    if ( key0 == "purpose" ) {
      vq = unescape(vq);
    }

    if ( key0 == "data_url" ) {
      vq = unescape(vq);
    }


    //try {
      if ( key0 == "Image" ) {
        $("#"+key0).html( "<img id=imgSrc src='" + vq + "'>" );

      } else if ( key0 == "data_url" ) {
        $("#"+key0).val( vq );
        enable_download_button();

      } else if ( key1 == "months" ) {
        select_months_from_str(vq);

      } else if ( key1 == "scale" ) {
        num2scale(Number(vq));

      } else if ( key1 == "scale2" ) {
        num2scale2(Number(vq));

      } else if ( key1 == "scale3" ) {
        num2scale3(Number(vq));

      } else if ( key1 == "anomaly" ) {
        num2checkbox(key1, Number(vq));

      } else {
        $("#"+key1).val(vq);
        $("#"+key1).change();
      }
    //} catch(err) {}
  }
}

// processQS2__
function processQS2() {
  queries = get_querystring();

  if (queries.length<1) {return;}

  var key0, key1, vq;

  if ( queries.hasOwnProperty("nVar") 
     && inputs.hasOwnProperty("nVar") )  {
    nVar = Number(queries["nVar"]) + nVarP;
  } else {
    nVar = nVar0;
  }

  for(var i=0; i<nVar; i++) {
    key0 = "model"+(i+1);
    key1 = "data"+(i+1);
    vq = fetchQValue(queries, key0);
    if (vq !==false) {
      vq = vq.replace("_", "/");
      $("#"+key1).val(vq);
      $("#"+key1).change();
    }
  
    key0 = "var"+(i+1);
    key1 = key0;
    vq = fetchQValue(queries, key0);
    if (vq !==false) {
      $("#"+key1).val(vq);
      $("#"+key1).change();
    }

    key0 = "pres"+(i+1);
    key1 = key0;
    vq = fetchQValue(queries, key0);
    if (vq !==false) {
      if (vq=="-999999") {
        vq = "N/A";
      }
      $("#"+key1).val(vq);
      $("#"+key1).change();
    }

    if ( dList[i]["isPressureRange"] ) {
      key0 = "pres"+(i+1)+"a";
      key1 = key0;
      vq = fetchQValue(queries, key0);
      if (vq !==false) {
        if (vq=="-999999") {
          vq = "N/A";
        }
        $("#"+key1).val(vq);
        $("#"+key1).change();
      }
    }
  }

  for (key0 in queries) {
    if ( key0.slice(0,5) == "model" ) { continue; }
    if ( key0.slice(0,3) == "var" ) { continue; }
    if ( key0.slice(0,4) == "pres" ) { continue; }

    vq = fetchQValue(queries, key0);
    if (vq ===false) { continue; }

    vq = vq.trim();
   
    // Image and data_url have no key1
    if ( key0 == "Image" || key0 == "data_url" ) {
      key1 = key0;
    } else {
      key1 = inputs[key0];
    }
    //vq = queries[key0];

    if ( key1 == "startT" || key1 == "endT" ) {
      vq = vq.slice(0,4) + "-" + vq.slice(4,6);
    }

    if ( key0 == "purpose" ) {
      vq = unescape(vq);
    }

    if ( key0 == "data_url" ) {
      vq = unescape(vq);
    }

    if (key1=="binMin2") {
      if (vq=="-999999") {
        document.getElementById("radioDef2").checked = true; 
      } else {
        document.getElementById("radioCus2").checked = true; 
      }
    } else if (key1=="binMin3") {
      if (vq=="-999999") {
        document.getElementById("radioDef3").checked = true; 
      } else {
        document.getElementById("radioCus3").checked = true; 
      }
    }

    //try {
      if ( key0 == "Image" ) {
        $("#"+key0).html( "<img id=imgSrc src='" + vq + "'>" );

      } else if ( key0 == "data_url" ) {
        $("#"+key0).val( vq );
        enable_download_button();

      } else if ( key1 == "months" ) {
        select_months_from_str(vq);

      } else if ( key1 == "scale" ) {
        num2scale(Number(vq));

      } else if ( key1 == "scale2" ) {
        num2scale2(Number(vq));

      } else if ( key1 == "scale3" ) {
        num2scale3(Number(vq));

      } else if ( key1 == "anomaly" ) {
        num2checkbox(key1, Number(vq));


      } else {
        $("#"+key1).val(vq);
        $("#"+key1).change();
      }
    //} catch(err) {}
  }  // loop key
}


// timeBound__() {
function timeBound(varNum, timeAffix) {
  var nVar = getNVar();
  if ( typeof varNum === 'undefined' ) {
    varNum = [];
    for (var i=0; i<nVar; i++) {
      varNum.push(i+1);
    } 
  }
  if (typeof timeAffix === 'undefined') { timeAffix = "";}
  var var_string1, data_string1;
  var timeS = 100001;
  var timeE = 300001;
  for (var ii=0; ii<varNum.length; ii++) {
    var i = varNum[ii];
    //alert(nVar);
    //alert(ii);
    //alert(i);
    var_string1 = $("#var"+(i)).val();
    data_string1 = $("#data"+(i)).val();
    //alert(var_string1 + " " + data_string1);
    timeS = Math.max( 
       Number(dataList[data_string1][2][var_string1][0]),
       timeS );
    timeE = Math.min( 
       Number(dataList[data_string1][2][var_string1][1]),
       timeE );
  }

  timeS = timeS.toString();
  timeE = timeE.toString();

  $("#startYear"+timeAffix).html("start year-month: (earliest:" + timeS.slice(0,4) + "-" + timeS.slice(4,6) + ")");
  $("#endYear"+timeAffix).html("end year-month: (latest:" + timeE.slice(0,4) + "-" + timeE.slice(4,6) + ")");
  $("#startYear"+timeAffix).data("time", Number(timeS));
  $("#endYear"+timeAffix).data("time", Number(timeE));
  //checkTimeL();
  //checkTimeH();
}

// addDataList_(ID) {
// modified from put_data()
function addDataList(ID) {
  var list1=document.getElementById("data"+ID);

  for(var key in dataList) {
    if (key.slice(0,5)==="group") {
      var og = document.createElement("OPTGROUP");
      og.setAttribute('label', dataList[key][0]);
      list1.add(og);

    } else {
      var toAdd = true;

      // whether the dataset has only 2D or only 3D variables
      if   ( dList[ID-1]["only2D"] 
        ||  dList[ID-1]["only3D"] ) {
        var dims = "";
        var varList2 = dataList[key][1];  
        for(var i=0; i<varList2.length; i++)   
          dims += String(varList[ varList2[i] ][2]);

        if   ( dList[ID-1]["only2D"] ) 
          if (dims.indexOf('2')==-1) toAdd = false;
        if   ( dList[ID-1]["only3D"] ) 
          if (dims.indexOf('3')==-1) toAdd = false;
      }
  
      // add to the option group
      if (toAdd) og.appendChild(new Option(key,key));
    }
  }
}

// addVarList_(ID) {
// modified from put_var()
function addVarList(ID) {
  //var var9 =  document.getElementById("var"+ID).value;
  var list1=document.getElementById("var"+ID);
  for (var i=list1.length-1; i>=0; i--) {
  list1.remove(i);
  }

  data_string =  document.getElementById("data"+ID).value;
  //alert("put_var: " + ID + " " + data_string);
  var varList2 = dataList[data_string][1];  

  if ( dList[ID-1]["only2D"] ) {
    // list only 2D variables
    for (var i=0; i<varList2.length; i++) {
      var k = varList2[i];
      if (varList[k][2]==2) list1.add(new Option(varList[k][0],k));
    }

  } else if ( dList[ID-1]["only3D"] ) {
    // list only 3D variables
    for (var i=0; i<varList2.length; i++) {
      var k = varList2[i];
      if (varList[k][2]==3) list1.add(new Option(varList[k][0],k));
    }

  } else {
    // list all 2D/3D variables
    for (var i=0; i<varList2.length; i++) {
      var k = varList2[i];
      list1.add(new Option(varList[k][0],k));
    }
  }

  //try { 
  //  $("var"+ID).val(var9);
  //} catch(err) {}

  var nVar = list1.options.length;
  if (nVar==0) {
    alert(data_string + " has no suitable variable.");
    document.getElementById("data"+ID).options[0].selected = true; 
    addVarList(ID);
  }
}

// addPres_(ID)
// same as select_var()
function addPres(ID)
{
  
  // if there isOnly2d is defined, there is no pressure widget.
  try {
    //var var_string = $("#var"+ID).val();
    //alert(is3D(ID));
    if (is3D(ID)) {
      enablePres(ID);
    } else {
      disablePres(ID);
    }
  }
  catch(err) {}
}

// enablePres_(ID) { 
// modified from enable_pres1()
function enablePres(ID) { 
  var var_string = $("#var"+ID).val();

  // whether pressureRange
  if (dList[ID-1]["isPressureRange"]) {
    var rangeStr = "range ";
  } else { 
    var rangeStr = "";
  }

  // pressure label
  var y=document.getElementById("pressureLabel"+ID);
  try {
    if (varList[var_string][1]==="ocean") {
      y.innerHTML = "ocean pressure " + rangeStr + "(dbar):";

    } else {
      y.innerHTML = "atmospheric pressure " + rangeStr + "(hPa):";
    }
  } catch(err) {}

  // pressure default 
  try {
    var x=document.getElementById("pres"+ID);
    x.value = dList[ID-1]["pressureDf"];
    x.disabled=false;
  } catch(err) {}
}

// enablePres2_(ID) { 
// modified from enable_pres1()
function enablePres2(ID) { 
  var var_string = $("#var"+ID).val();
  //alert( dList[ID-1]["isPressureRange"] );

  // whether pressureRange
  if (dList[ID-1]["isPressureRange"]) {
    var rangeStr = "range ";
  } else { 
    var rangeStr = "";
  }

  // pressure label
  var y=document.getElementById("pressureLabel"+ID);
  try {
    if (varList[var_string][1]==="ocean") {
      y.innerHTML = "ocean pressure " + rangeStr + "(dbar):";
      var pressureDf = dList[ID-1]["pressureDfOcean"];
      if (dList[ID-1]["isPressureRange"]) {
        var pressureDfa = dList[ID-1]["pressureDfaOcean"];
      }
    } else {
      y.innerHTML = "atmospheric pressure " + rangeStr + "(hPa):";
      var pressureDf = dList[ID-1]["pressureDf"];
      if (dList[ID-1]["isPressureRange"]) {
        var pressureDfa = dList[ID-1]["pressureDfa"];
      }
    }
  } catch(err) {}

  // pressure default 
  try {
    var x=document.getElementById("pres"+ID);
    x.value = pressureDf;
    x.disabled=false;
    if (dList[ID-1]["isPressureRange"]) {
      var x=document.getElementById("pres"+ID+"a");
      x.value = pressureDfa;
      x.disabled=false;
    }
  } catch(err) {}
}

// disablePres_(ID) {
// same as disable_pres1()
function disablePres(ID) {
  try {
    var x;
    x=document.getElementById("pres"+ID);
    x.value = "N/A";
    x.disabled=true;
    var y=document.getElementById("pressureLabel"+ID);
    y.innerHTML = "pressure:";
  }
  catch(err) {}
}

// disablePres2_(ID) {
function disablePres2(ID) {
  try {
    var x;
    x=document.getElementById("pres"+ID);
    x.value = "N/A";
    x.disabled=true;
    var y=document.getElementById("pressureLabel"+ID);
    y.innerHTML = "pressure:";

    if (dList[ID-1]["isPressureRange"]) {
      var x=document.getElementById("pres"+ID+"a");
      x.value = "N/A";
      x.disabled=true;
      y.innerHTML = "pressure range:";
    }
  }
  catch(err) {}
}


// checkTimeL_() {
function checkTimeL(timeAffix) {
  if (typeof timeAffix === 'undefined') { timeAffix = "";}

  var t1a = $("#startT"+timeAffix).val();
  var t1 = Number( t1a.replace("-", "") );

  var t0 = $("#startYear"+timeAffix).data("time");
  var t0a = String(t0);
  t0a = t0a.slice(0,4) + "-" + t0a.slice(4,6);

  if ( t1a=="" ) {
    $("#startT"+timeAffix).val(t0a);
    return;
  }

  //alert(t0 + " " + t1);
  if ( t1 < t0 ) {
    alert("The entered time " + t1a + " is beyond the left time bound." + "\nThe start time will be set to " + t0a + ".");

    $("#startT"+timeAffix).val(t0a);
  }

}

// checkTimeH_() {
function checkTimeH(timeAffix) {
  if (typeof timeAffix === 'undefined') { timeAffix = "";}
  var t1a = $("#endT"+timeAffix).val();
  var t1 = Number( t1a.replace("-", "") );

  var t0 = $("#endYear"+timeAffix).data("time");
  var t0a = String(t0);
  t0a = t0a.slice(0,4) + "-" + t0a.slice(4,6);

  if ( t1a=="" ) {
    $("#endT"+timeAffix).val(t0a);
    return;
  }

  //alert(t0 + " " + t1);
  if ( t1 > t0 ) {
    alert("The entered time " + t1a + " is beyond the right time bound." + "\nThe end time will be set to " + t0a + ".");

    $("#endT"+timeAffix).val(t0a);
  }
}

// parseNum_(num1) {
function parseNum(num1) {
  var num2 = "";
  if (isNaN(Number(num1))) { 
    num2 = naValue; 
  } else {
    num2 = num1; 
  }
  return num2;
}

// cmacBase3__

// makeUrl3__
function makeUrl3(toServer) {
  toServer = typeof toServer !== 'undefined' ? toServer:false;

  var vq, key0, key1, nVar;
  var temp1 = "";

  nVar = getNVar();
  for(var i=0; i<nVar; i++) {
    key0 = "model"+(i+1);
    key1 = "data"+(i+1);
    vq = $("#"+key1).val();
    vq = vq.replace("/", "_");
    if ( toServer ) {
      vq = vq.toLowerCase();
    }
    temp1 += key0 + "=" + vq + "&";

    key0 = "var"+(i+1);
    key1 = key0;
    vq = $("#"+key1).val();
    temp1 += key0 + "=" + vq + "&";

    key0 = "pres"+(i+1);
    key1 = key0;
    vq = $("#"+key1).val();
    vq = parse_pres(vq);
    temp1 += key0 + "=" + vq + "&";
  }

  for (key0 in mapping) {
    if (!mapping.hasOwnProperty(key0)) { continue; }

    key1 = mapping[key0].key1;

    try {
      //vq = $("#"+key1).val();
      vq = mapping[key0].fromHtml();
    } catch(err) {
      vq = "";
    }

    // the alert here generates an error:
    // alert(key0+"  "+vq);

    //if ( key1 == "startT" || key1 == "endT" ) {
    //  vq = vq.replace("-", "");

    //} else if ( key1 == "purpose" ) {
      // not to do "purpose" if it is empty
      //if ( vq=="" && !toServer ) {
      //  continue;
      //}
    //  vq = escape(vq);

    //} else if ( key0 == "nVar" ) {
    //  vq = nVarI + nVarP;
    //  }

    if ( key1 == "months" ) {
      vq = getMonthStr();

    } else if ( key1 == "scale" ) {
      vq = scale2num();

    } else if ( key1 == "scale2" ) {
      vq = scale2num2();

    } else if ( key1 == "scale3" ) {
      vq = scale2num3();

    } else if ( key1 == "anomaly" ) {
      vq = checkbox2num(key1);

    }
/*
      if ( key0.slice(0,4) == "pres" ) {
        if ( Number(v1q) == NaN ) {
          vq = "-999999";
        }
      }
*/
    temp1 += key0 + "=" + vq + "&";
  }

  temp1 = temp1.slice(0,-1);

  if (toServer) { return temp1; }

  else {
    temp1 = document.location.href.split('?')[0] + "?" + temp1;
    return temp1;
  }
}

// makeUrl3a__
function makeUrl3a() {
  var vq, key0, key1; 
  var temp1 = makeUrl3();
  //alert(temp1);
  try {
    vq = document.querySelectorAll('#Image img')[0].src;
  } catch(err) { }

    //var temp2 = typeof vq;
    //alert(temp2);
    //alert(vq);
  if (typeof vq !== 'undefined') {
    key0 = "Image";
    //alert("&" + key0 + "=" + vq);
    temp1 += "&" + key0 + "=" + vq;
  }

  //try {
    key0 = "data_url";
    key1 = key0;
    vq = $("#"+key1).val();
    if (vq.length > 20) {
      vq = escape(vq);
      temp1 += "&" + key0 + "=" + vq;
    }
  //} catch(err) { }

  return temp1;
}


// processQS3__
function processQS3() {
  queries = get_querystring();

  if (queries.length<1) {return;}

  var key0, key1, vq, nVar;

  if ( queries.hasOwnProperty("nVar") 
     && mapping.hasOwnProperty("nVar") )  {
    nVar = Number(queries["nVar"]) + nVarP;
  } else {
    nVar = nVar0;
  }

  for(var i=0; i<nVar; i++) {
    key0 = "model"+(i+1);
    key1 = "data"+(i+1);
    vq = fetchQValue(queries, key0);
    if (vq !==false) {
      vq = vq.replace("_", "/");
      $("#"+key1).val(vq);
      $("#"+key1).change();
    }
  
    key0 = "var"+(i+1);
    key1 = key0;
    vq = fetchQValue(queries, key0);
    if (vq !==false) {
      $("#"+key1).val(vq);
      $("#"+key1).change();
    }

    key0 = "pres"+(i+1);
    key1 = key0;
    vq = fetchQValue(queries, key0);
    if (vq !==false) {
      if (vq=="-999999") {
        vq = "N/A";
      }
      $("#"+key1).val(vq);
      $("#"+key1).change();
    }
  }

  for (key0 in queries) {
    if ( key0.slice(0,5) == "model" ) { continue; }
    if ( key0.slice(0,3) == "var" ) { continue; }
    if ( key0.slice(0,4) == "pres" ) { continue; }

    vq = fetchQValue(queries, key0);
    if (vq ===false) { continue; }

    vq = vq.trim();
   
    // Image and data_url have no key1
    if ( key0 == "Image" || key0 == "data_url" ) {
      key1 = key0;
    } else {
      key1 = mapping[key0].key1;
    }
    //vq = queries[key0];

    if ( key0 == "data_url" ) {
      vq = unescape(vq);
    }


    //try {
      if ( key0 == "Image" ) {
        $("#"+key0).html( "<img id=imgSrc src='" + vq + "'>" );

      } else if ( key0 == "data_url" ) {
        $("#"+key0).val( vq );
        enable_download_button();
        includeDataUrl = true;
        dataUrl = vq

      } else if ( key1 == "months" ) {
        select_months_from_str(vq);

      } else if ( key1 == "scale" ) {
        num2scale(Number(vq));

      } else if ( key1 == "scale2" ) {
        num2scale2(Number(vq));

      } else if ( key1 == "scale3" ) {
        num2scale3(Number(vq));

      } else if ( key1 == "anomaly" ) {
        num2checkbox(key1, Number(vq));

      } else {
        mapping[key0].toHtml(vq);
      }
    //} catch(err) {}
  }
}

// displayUrl3_ {
function displayUrl3() {
  var temp1 = makeUrl3();
  //alert(temp1);
  //document.getElementById("actionUrl").innerHTML = temp1;
  document.getElementById("actionUrl").value = temp1;
}

function displayUrl3a() {
  var temp1 = makeUrl3a();
  document.getElementById("actionUrl").value = temp1;
}

// cmacBase4__
// makeUrl4__
function makeUrl4(toServer) {
  toServer = typeof toServer !== 'undefined' ? toServer:false;

  var vq, key0, key1, nVar;
  var temp1 = "";

  nVar = getNVar();
  for(var i=0; i<nVar; i++) {
    key0 = "model"+(i+1);
    key1 = "data"+(i+1);
    vq = $("#"+key1).val();
    vq = vq.replace("/", "_");
    temp1 += key0 + "=" + vq + "&";

    key0 = "var"+(i+1);
    key1 = key0;
    vq = $("#"+key1).val();
    temp1 += key0 + "=" + vq + "&";

    key0 = "pres"+(i+1);
    key1 = key0;
    vq = $("#"+key1).val();
    vq = parse_pres(vq);
    temp1 += key0 + "=" + vq + "&";
  }

  for (key0 in mapping) {
    if (!mapping.hasOwnProperty(key0)) { continue; }

    key1 = mapping[key0].key1;

    try {
      //vq = $("#"+key1).val();
      vq = mapping[key0].fromHtml();
    } catch(err) {
      vq = "";
    }

    temp1 += key0 + "=" + vq + "&";
  }

  temp1 = temp1.slice(0,-1);

  if (toServer) { 
    temp1 += "fromPage=" + document.location.href.split('?')[0];
    return temp1; 
  }

  else {
    temp1 = document.location.href.split('?')[0] + "?" + temp1;
    return temp1;
  }
}

// makeUrl4a__
function makeUrl4a() {
  var vq, key0, key1; 
  var temp1 = makeUrl4();
  //alert(temp1);
  try {
    vq = document.querySelectorAll('#Image img')[0].src;
  } catch(err) { }

    //var temp2 = typeof vq;
    //alert(temp2);
    //alert(vq);
  if (typeof vq !== 'undefined') {
    key0 = "Image";
    //alert("&" + key0 + "=" + vq);
    temp1 += "&" + key0 + "=" + vq;
  }

  //try {
    key0 = "data_url";
    key1 = key0;
    vq = $("#"+key1).val();
    if (vq.length > 20) {
      vq = escape(vq);
      temp1 += "&" + key0 + "=" + vq;
    }
  //} catch(err) { }

  return temp1;
}


// processQS4__
function processQS4() {
  queries = get_querystring();

  if (queries.length<1) {return;}

  var key0, key1, vq, nVar;

  if ( queries.hasOwnProperty("nVar") 
     && mapping.hasOwnProperty("nVar") )  {
    nVar = Number(queries["nVar"]) + nVarP;
  } else {
    nVar = nVar0;
  }

  for(var i=0; i<nVar; i++) {
    key0 = "model"+(i+1);
    key1 = "data"+(i+1);
    vq = fetchQValue(queries, key0);
    if (vq !==false) {
      vq = vq.replace("_", "/");
      $("#"+key1).val(vq);
      $("#"+key1).change();
    }
  
    key0 = "var"+(i+1);
    key1 = key0;
    vq = fetchQValue(queries, key0);
    if (vq !==false) {
      $("#"+key1).val(vq);
      $("#"+key1).change();
    }

    key0 = "pres"+(i+1);
    key1 = key0;
    vq = fetchQValue(queries, key0);
    if (vq !==false) {
      if (vq=="-999999") {
        vq = "N/A";
      }
      $("#"+key1).val(vq);
      $("#"+key1).change();
    }
  }

  for (key0 in queries) {
    if ( key0.slice(0,5) == "model" ) { continue; }
    if ( key0.slice(0,3) == "var" ) { continue; }
    if ( key0.slice(0,4) == "pres" ) { continue; }

    vq = fetchQValue(queries, key0);
    if (vq ===false) { continue; }

    vq = vq.trim();
   
    // Image and data_url have no key1
    if ( key0 == "Image" || key0 == "data_url" ) {
      key1 = key0;
    } else {
      key1 = mapping[key0].key1;
    }
    //vq = queries[key0];

    if ( key0 == "data_url" ) {
      vq = unescape(vq);
    }


    //try {
      if ( key0 == "Image" ) {
        $("#"+key0).html( "<img id=imgSrc src='" + vq + "'>" );

      } else if ( key0 == "data_url" ) {
        $("#"+key0).val( vq );
        enableButton("download_data");
        //includeDataUrl = true;
        dataUrl = vq

      } else {
        mapping[key0].toHtml(vq);
      }
    //} catch(err) {}
  }
}

// displayUrl4_ {
function displayUrl4() {
  var temp1 = makeUrl4();
  //alert(temp1);
  //document.getElementById("actionUrl").innerHTML = temp1;
  document.getElementById("actionUrl").value = temp1;
}

function displayUrl3a() {
  var temp1 = makeUrl3a();
  document.getElementById("actionUrl").value = temp1;
}

// ==url_classes

// urlDirect_() {
function urlDirect() {
  this.key0 = key99;
  this.key1 = arg99[0];
  this.fromHtml = function(){
    return $("#"+this.key1).val();
  }
  this.toHtml = function(vq){
    $("#"+this.key1).val(vq);
    $("#"+this.key1).change();
  }
}

// urlCheckbox_() {
// it is the same as checkbox2num()
function urlCheckbox() {
  this.key0 = key99;
  this.key1 = arg99[0];
  this.fromHtml = function(){
    if ( document.getElementById(this.key1).checked ) {
      return 1;
    } else {
      return 0;
    }
  }
  this.toHtml = function(vq){
    if ( Number(vq)==1 ) {
      document.getElementById(this.key1).checked = true;
    } else {
      document.getElementById(this.key1).checked = false;
    }
  }
}


// urlDash_() {
function urlDash() {
  this.key0 = key99;
  this.key1 = arg99[0];
  this.fromHtml = function(){
    var vq = $("#"+this.key1).val();
    vq = vq.replace("-", "");
    return vq;
  }
  this.toHtml = function(vq){
    vq = vq.slice(0,4) + "-" + vq.slice(4,6);
    $("#"+this.key1).val(vq);
    $("#"+this.key1).change();
  }
}

// urlEscape_() {
function urlEscape() {
  this.key0 = key99;
  this.key1 = arg99[0];
  this.fromHtml = function(){
    var vq = $("#"+this.key1).val();
    vq = escape(vq);
    return vq;
  }
  this.toHtml = function(vq){
    vq = unescape(vq);
    $("#"+this.key1).val(vq);
    $("#"+this.key1).change();
  }
}

// urlRadioTwo_() {
function urlRadioTwo() {
  this.key0 = key99;
  this.key1 = arg99[0];
  this.radio1 = arg99[2];
  this.radio2 = arg99[3];
  this.fromHtml = function() {
    if ( document.getElementById(this.radio1).checked ) {
      return "1";
    } else { 
      return "0";
    }
  }
  this.toHtml = function(vq) {
    vq = Number(vq);
    //console.log(this.radio1);
    if (vq == 1) { 
      document.getElementById(this.radio1).checked = true;
      document.getElementById(this.radio2).checked = false;
    } else { 
      document.getElementById(this.radio1).checked = false;
      document.getElementById(this.radio2).checked = true;
    }
  }
}

// urlDataUrl_() {
function urlDataUrl() {
  var vq;
  this.key0 = key99;
  this.key1 = arg99[0];
  this.fromHtml = function(){
    //console.log(document.getElementById("download_data").disabled);
    //if (document.getElementById("download_data").disabled == false) {
    if (includeDataUrl) {
      vq = dataUrl;
    } else {
      vq = "";
    }
    return vq;
  }

  this.toHtml = function(vq){
    vq = unescape(vq);
    $("#"+this.key1).val(vq);
    $("#"+this.key1).change();
  }
}

// urlMonths_() {
function urlMonths() {
  var vq;
  this.key0 = key99;
  this.key1 = arg99[0];
  this.fromHtml = function(){
    vq = getMonthStr();
    return vq;
  }

  this.toHtml = function(vq){
    select_months_from_str(vq);
  }
}

// urlScale1_() {
function urlScale1() {
  var vq;
  this.key0 = key99;
  this.key1 = arg99[0];
  this.fromHtml = function(){
    return scale2num1();
  }

  this.toHtml = function(vq){
    var vq1 = Number(vq);
    num2scale1(vq1);
  }
}

// urlScale2_() {
function urlScale2() {
  var vq;
  this.key0 = key99;
  this.key1 = arg99[0];
  this.fromHtml = function(){
    return scale2num2();
  }

  this.toHtml = function(vq){
    var vq1 = Number(vq);
    num2scale2(vq1);
  }
}

// urlScale3_() {
function urlScale3() {
  var vq;
  this.key0 = key99;
  this.key1 = arg99[0];
  this.fromHtml = function(){
    return scale2num3();
  }

  this.toHtml = function(vq){
    var vq1 = Number(vq);
    num2scale3(vq1);
  }
}


