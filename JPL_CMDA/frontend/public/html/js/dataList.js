// modelName: [category, listOfVar],
var groupList={
"group1":         ["Model: Historical"],
"group2":         ["Model: AMIP"],
"group3":         ["Observation"],
"group4":         ["Reanalysis"],
};

var dataList={
"group1":         ["Model: Historical"],
"GFDL/ESM2G":     ["Model: Historical",      ["pr", "clt", "ts", "tos", "uas", "vas", "sfcWind", "zos", "lai", "rlds", "rlus", "rldscs", "rlut", "rlutcs", "ta", "hus", "cli", "clw", "wap", "hur", ] ],       
"GISS/E2-H":      ["Model: Historical",      ["pr", "clt", "ts", "tos", "uas", "vas", "sfcWind", "rlds", "rsds", "rlus", "rsus", "rldscs", "rsdscs", "rsuscs", "rsdt", "rlut", "rsut", "rlutcs", "rsutcs", "cli", "clw", "wap", "hur", ] ],      
"GISS/E2-R":      ["Model: Historical",      ["pr", "clt", "ts", "tos", "uas", "vas", "sfcWind", "rsds", "rlus", "rsus", "rldscs", "rsdscs", "rsuscs", "rsdt", "rlut", "rsut", "rlutcs", "rsutcs", "cli", "clw", "wap", "hur", ] ],      
"NCAR/CAM5":      ["Model: Historical",      ["pr", "clt", "ts", "tos", "sfcWind", "zos", "lai", "rlds", "rsds", "rlus", "rsus", "rsdscs", "rsuscs", "rsdt", "rlut", "rsut", "rlutcs", "rsutcs", "cli", "clw", "wap", "hur", ] ],      
"NCC/NORESM":     ["Model: Historical",      ["pr", "clt", "ts", "tos", "uas", "vas", "zos", "lai", "rlds", "rsds", "rlus", "rsus", "rldscs", "rsdscs", "rsuscs", "rsdt", "rlut", "rsut", "rlutcs", "rsutcs", "ta", "hus", "cli", "clw", "wap", "hur", ] ],       
"UKMO/HadGEM2-ES":["Model: Historical",      ["pr", "clt", "ts", "uas", "vas", "sfcWind", "zos", "lai", "rlds", "rsds", "rlus", "rsus", "rldscs", "rsdscs", "rsuscs", "rsdt", "rlut", "rsut", "rlutcs", "rsutcs", "cli", "clw", "wap", "hur", ] ],            
//                [ 
"group2":         ["Model: AMIP"],
"CCCMA/CANAM4":   ["Model: AMIP",            ["ts", "uas", "vas", "sfcWind", "rlds", "rsds", "rlus", "rsus", "rldscs", "rsdscs", "rsuscs", "rsdt", "rlut", "rsut", "rlutcs", "rsutcs", "cli", "clw", ] ],         
"CSIRO/MK3.6":    ["Model: AMIP",            ["pr", "clt", "ts", "uas", "vas", "sfcWind", "rlds", "rsds", "rlus", "rsus", "rldscs", "rsdscs", "rsuscs", "rsdt", "rlut", "rsut", "rlutcs", "rsutcs", "cli", "clw", "wap", "hur", ] ],        
"GFDL/CM3":       ["Model: AMIP",            ["pr", "clt", "ts", "uas", "vas", "rlds", "rsds", "rlus", "rsus", "rldscs", "rsdscs", "rsuscs", "rsdt", "rlut", "rsut", "rlutcs", "rsutcs", "ta", "hus", "cli", "clw", "wap", "hur", ] ],     
"IPSL/CM5A-LR":   ["Model: AMIP",            ["pr", "clt", "ts", "lai", "rlds", "rsds", "rlus", "rsus", "rldscs", "rsdscs", "rsuscs", "rsdt", "rlut", "rsut", "rlutcs", "rsutcs", "cli", "clw", "wap", "hur", ] ],         
"MIROC/MIROC5":   ["Model: AMIP",            ["pr", "clt", "ts", "uas", "vas", "sfcWind", "lai", "rlds", "rsds", "rlus", "rsus", "rldscs", "rsdscs", "rsuscs", "rsdt", "rlut", "rsut", "rlutcs", "rsutcs", "cli", "clw", "wap", "hur", ] ],         
"UKMO/HadGEM2-A": ["Model: AMIP",            ["pr", "clt", "ts", "uas", "vas", "sfcWind", "rlds", "rsds", "rlus", "rsus", "rldscs", "rsdscs", "rsuscs", "rsdt", "rlut", "rsut", "rlutcs", "rsutcs", "cli", "clw", "wap", "hur", ] ],           
//                [ 
"group3":         ["Observation"],
"NASA/GRACE":     ["Observation", ["zl", "zo", ] ],            
"NASA/MODIS":     ["Observation", ["clt", "lai", ] ],
"NASA/AMSRE":     ["Observation", ["tos", ] ],
"NASA/TRMM":      ["Observation", ["pr", ] ],
"NASA/GPCP":      ["Observation", ["pr", ] ],
"NASA/QuikSCAT":  ["Observation", ["uas", "vas", "sfcWind", ] ],
"NASA/AVISO":     ["Observation", ["zos", ] ],
"NOAA/NODC":      ["Observation", ["ohc700", "ohc2000", ] ],
"NASA/CERES":     ["Observation", ["rlds", "rsds", "rlus", "rsus", "rldscs", "rsdscs", "rsuscs", "rsdt", "rlut", "rsut", "rlutcs", "rsutcs", ] ],
"NASA/AIRS":      ["Observation", ["ta", "hus", ] ],
"NASA/MLS":       ["Observation", ["ta", "hus", ] ],
"ARGO/ARGO":      ["Observation", ["ot", "os", ] ],           
//
"group4":         ["Reanalysis"],
"ECMWF/interim":  ["Reanalysis",  ["clt", "tos", "wap", "hur", ] ], 
};
