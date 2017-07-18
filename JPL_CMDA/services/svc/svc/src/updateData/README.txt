. updateData is the parent caller
. updateData1 updateData2 updateData3 represent 3 steps
. updateData1 is scanner
  scan the dir structure and data file names to form a dictionary
. updateData2 
  uses the dictionary to generate des file for Ferret
  in order to link several data files into logically one
  create des file to put under data_2017/des/.
. updateData3 
  generate the js file from a template
  the js is used by the html front pages
  dataList1.js is for Chengxing
  dataList2.js is for Benyang
