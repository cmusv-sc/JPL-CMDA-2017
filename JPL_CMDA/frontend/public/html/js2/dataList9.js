// modelName: [category, listOfVar],
var groupList={
"group1":         ["Model: Historical"],
"group2":         ["Model: AMIP"],
"group3":         ["Observation"],
"group4":         ["Reanalysis"],
"group5":         ["WRF"],
};

var dataList={
"group1":         ["PODAAC"],
"PODAAC/MUR_SST":     ["Model: Historical",      ["analysed_sst", ], {'analysed_sst': [20020601, 20160630],} ],       
"PODAAC/AVHRR_SST":     ["Model: Historical",      ["analysed_sst", ], {'analysed_sst': [19810901, 20161101],} ],       
"PODAAC/SSH":     ["Model: Historical",      ["ssha", ], {'ssha': [19500103, 20090627],} ],       
"PODAAC/WIND":     ["Model: Historical",      ["uvwnd","uwnd","vwnd","wspd" ], {'uvwnd': [19870705, 20111227],'uwnd': [19870705, 20111227],'vwnd': [19870705, 20111227],'wspd': [19870705, 20111227],} ],       
"PODAAC/CURRENT":     ["Model: Historical",      ["uv","u","v",], {'uv': [19921021, 20091226],'u': [19921021, 20091226],'v': [19921021, 20091226],} ],       
"PODAAC/AVISO_SSH":     ["Model: Historical",      ["zos",], {'zos': [19921016, 20101216],} ],       
};

//"JPL/CURRENT":     ["Model: Historical",      ["uv","u","v",], {'uv': [19921021, 20151226],'u': [19921021, 20151226],'v': [19921021, 20151226],} ],       
