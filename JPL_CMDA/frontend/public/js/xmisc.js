xmisc = {};

// use parameters in attributes (list) to extract valid points from data (list)
xmisc.get_valid_data_hdf4 = function(attrs, data) {

    var fillValue = null;
    //var missingValue = null;
    var scaleFactor = null;
    var offset = null;
    var validRange = null;
    var count = 0;
    for (var i=0; i<attrs.length; i++) {
        var attr = attrs[i];
        var name = attr["name"];
        var value = attr["value"];
        if (name == "_FillValue") {
            fillValue = value;
            count += 1;
        }
        if (name == "scale_factor") {
            scaleFactor = value;
            count += 1;
        }
        if (name == "add_offset") {
            offset = value;
            count += 1;
        }
        if (name == "valid_range") {
            validRange = value;
            count += 1;
        }
    }

    // insist on seeing all 4 of fillValue, scaleFactor, offset, validRange
    //if (count != 4)
    if (scaleFactor == null || offset == null || validRange == null)
        return this.get_valid_data_default(data);

    // sometimes validRange is bad, such as [0, -1], e.g.,
    // http://oscar1.jpl.nasa.gov/data/cache/ladsweb.nascom.nasa.gov/allData/5/MOD05_L2/2008/123/MOD05_L2.A2008123.0405.005.2008124113323.hdf/Quality_Assurance_Infrared/?output=json
    var validRangeIsOkay= true;
    if (validRange[0] > validRange[1])
        var validRangeIsOkay = false;

    var z = [];
    for (var i=0; i<data.length; i++) {
        if (validRangeIsOkay && data[i] < validRange[0])
            continue;
        if (validRangeIsOkay && data[i] > validRange[1])
            continue;
        z.push([i, data[i]*scaleFactor+offset]);
    }

    return z;
}

// use parameters in attributes (list) to extract valid points from data (list)
xmisc.get_valid_data_hdf5 = function(attrs, data) {

    var fillValue = null;
    var missingValue = null;
    //var scaleFactor = null;
    //var offset = null;
    //var validRange = null;
    var count = 0;
    for (var i=0; i<attrs.length; i++) {
        var attr = attrs[i];
        var name = attr["name"];
        var value = attr["value"];
        if (name == "_FillValue") {
            fillValue = value;
            count += 1;
        }
        if (name == "MissingValue") {
            missingValue = value;
            count += 1;
        }
        /*
        if (name == "scale_factor") {
            scaleFactor = value;
            count += 1;
        }
        if (name == "add_offset") {
            offset = value;
            count += 1;
        }
        if (name == "valid_range") {
            validRange = value;
            count += 1;
        }
        */
    }

    // insist on seeing all 2 of fillValue, missingValue
    if (count != 2)
        return this.get_valid_data_default(data);

    var z = [];
    for (var i=0; i<data.length; i++) {
        if (data[i] == missingValue)
            continue;
        //z.push([i, data[i]*scaleFactor+offset]);
        z.push([i,data[i]]);
    }

    return z;
}

// use parameters in attributes (list) to extract valid points from data (list)
// specifically for aws
xmisc.get_valid_data_nc_aws = function(attrs, data) {

    var fillValue = null;
    //var missingValue = null;
    var scaleFactor = 1.0;
    //var offset = null;
    //var validRange = null;
    var count = 0;
    for (var i=0; i<attrs.length; i++) {
        var attr = attrs[i];
        var name = attr["name"];
        var value = attr["value"];
        if (name == "_FillValue") {
            fillValue = value;
            count += 1;
        }
        if (name == "scale_factor") {
            scaleFactor = value;
            count += 1;
        }
        //if (name == "add_offset") {
        //    offset = value;
        //    count += 1;
        //}
        //if (name == "valid_range") {
        //    validRange = value;
        //    count += 1;
        //}
    }

    // insist on seeing all 4 of fillValue, scaleFactor, offset, validRange
    //if (count != 4)
    if (scaleFactor == null)
        return this.get_valid_data_default(data);

    var z = [];
    for (var i=0; i<data.length; i++) {
        if (fillValue != null && data[i] == fillValue)
            continue;
        z.push([i, data[i]*scaleFactor]);
    }

    return z;
}

xmisc.get_valid_data_default = function(data) {
    var min = -10000;
    var max = 10000;

    var z = [];
    for (var i=0; i<data.length; i++) {
        if (data[i] < min)
            continue;
        if (data[i] > max)
            continue;
        z.push([i,data[i]]);
    }
    
    return z;
}

xmisc.get_valid_data = function(w10nType, attrs, data) {

    if (w10nType == "hdf4" || w10nType == "hdf4.basic")
        return this.get_valid_data_hdf4(attrs, data);

    if (w10nType == "hdf5" || w10nType == "hdf5.basic")
        return this.get_valid_data_hdf5(attrs, data);

    if (w10nType == "nc")
        return this.get_valid_data_nc_aws(attrs, data);

    return this.get_valid_data_default(data);
}

xmisc.get_series1 = function(x, y, min, max) {
    //var min = -10000;
    //var max = 10000;

    var data = [];

    if (x == null)
        return {error:"x is null", data:data};
    if (y == null)
        return {error:"y is null", data:data};
    if (x.length != y.length)
        return {error:"x and y are not of the same size", data:data};

    var data = [];
    for (var i=0; i<x.length; i++) {
        if (x[i] <= min || x[i] >= max)
            continue;
        if (y[i] <= min || y[i] >= max)
            continue;
        data.push([x[i],y[i]]);
    }
    
    return {error:null, data:data};
}

/*
xmisc.mask = function(a, allowRange, rejectList, value) {
    var x = this.select_by_range(a, allowRange, value, false);
    x = this.select_by_list(a, rejectList, value, true);
    return x;
}
*/

// a: array
// range: [r0, r1]
// value: set to value if out of range
// negate: boolean to negate selection
// return: array with out-of-range members as value
xmisc.select_by_range = function(a, range, value, negate) {
    if (!range)
        return a;

    var r0 = range[0];
    var r1 = range[1];

    var b = [];
    var i, x, y;
    for (i=0; i<a.length; i++) {
        x = a[i];
        if (x >= r0 && x <= r1) {
            x = (negate) ? value : x;
        } else {
            x = (negate) ? x: value;
        }
        b.push(x);
    }
    return b;
}

xmisc.isOneOf = function(x, a) {
    for (var i=0; i<a.length; i++) {
        if (x == a[i])
            return true;
    }
    return false;
}

// a: array
// list: [val0, val1, ...], list to mask
// value: set to value if member is one of list
// negate: boolean to negate selection
// return: array with members in list as value
xmisc.select_by_list = function(a, list, value, negate) {
    if (!list)
        return a;

    var b = []
    var i, x;
    for (i=0; i<a.length; i++) {
        x = a[i];
        if (this.isOneOf(x, list)) {
            x = (negate) ? value : x;
        } else {
            x = (negate) ? x : value;
        }
        b.push(x);
    }
}

xmisc.filter = function(x, filter) {
    if (!filter)
        return x;
    z = [];
    var lower = null;
    var upper = null;
    if (filter.validRange) {
        lower = filter.validRange[0];
        upper = filter.validRange[1];
    }
    var mask = [];

    for (var i=0; i<x.length; i++) {
        if (filter.validRange) {
            if (x[i] < filter.validRange[0] || x[i] > filter.validRange[1]) {
                z.push(null);
            } else {
                z.push(x[i]);
            }
            continue;
        }
        if (filter.MaskedValues) {
            continue;
        }
        z.push(x[i]);
    }
}

xmisc.get_series = function(x, y) {

    var data = [];

    if (x == null)
        return {error:"x is null"};
    if (y == null)
        return {error:"y is null"};
    if (x.length != y.length)
        return {error:"x and y are not of the same size"};

    var data = [];
    for (var i=0; i<x.length; i++) {
        data.push([x[i],y[i]]);
    }
    
    return {error:null, data:data};
}
