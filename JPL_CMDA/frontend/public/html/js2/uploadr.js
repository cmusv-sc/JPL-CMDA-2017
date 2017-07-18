/******************************************************************************
 * HTML5 Multiple File Uploader Demo                                          *
 ******************************************************************************/

// Constants
var MAX_UPLOAD_FILE_SIZE = 20 * 1024*1024; // 1 MB
var UPLOAD_URL = "/upload";
var NEXT_URL   = "/files/";

// List of pending files to handle when the Upload button is finally clicked.
var PENDING_FILES  = [];



function doUpload() {
    $("#progress").show();
    var $progressBar   = $("#progress-bar");

    console.log('in doUpload');
    // Gray out the form.
    //$("#uploadForm :input").attr("disabled", "disabled");

    // Initialize the progress bar.
    $progressBar.css({"width": "0%"});

    // Collect the form data.
    fd = collectFormData();

    // Attach the files.
    for (var i = 0, ie = PENDING_FILES.length; i < ie; i++) {
        // Collect the other form data.
        fd.append("file", PENDING_FILES[i]);
    }

    // Inform the back-end that we're doing this over ajax.
    //fd.append("__ajax", "true");

    //var xhr = $.ajax({
    $.ajax({
        //xhr: function() {
        //    var xhrobj = $.ajaxSettings.xhr();
        //    if (xhrobj.upload) {
        //        xhrobj.upload.addEventListener("progress", function(event) {
        //            var percent = 0;
        //            var position = event.loaded || event.position;
        //            var total    = event.total;
        //            if (event.lengthComputable) {
        //                percent = Math.ceil(position / total * 100);
        //            }

        //            // Set the progress bar.
        //            $progressBar.css({"width": percent + "%"});
        //            $progressBar.text(percent + "%");
        //        }, false)
        //    }
        //    return xhrobj;
        //},
        //method: "POST",
        type: "POST",
        url: "http://cmda-test.jpl.nasa.gov:8090/fileUpload2",
        data: fd,
        contentType: false,
        cache: false,
        processData: false,
        //async: false,
        success: function(data) {
          //alert(data.message + '\n' + data.check);
          console.log(data.success);
          if (data.success==true) {
            $("#onlineFileCheckProgress").text('File check finished.'); 
            //console.log(data.varList);
            console.log(data.varDict);
          
            vueApp.uploadFileVarDict = data.varDict;
            vueApp.uploadFileVarList = data.varList;
            vueApp.uploadFileDimList = data.dimList;
            vueApp.varB = vueApp.uploadFileVarList[0];
            vueApp.uploadFileShow = true;
          } else {
            $("#onlineFileCheckProgress").text('File check failed.'); 
            vueApp.onlineFileShow = false;
          }
            //$progressBar.css({"width": "100%"});
            //data = JSON.parse(data);

            // How'd it go?
            if (data.status === "error") {
                // Uh-oh.
                window.alert(data.msg);
                $("#uploadForm :input").removeAttr("disabled");
                return;
            }
            else {
                // Ok! Get the UUID.
                //var uuid = data.msg;
                //window.location = NEXT_URL + uuid;
            }
        }, // success
    });  // ajax
}  // upload()


function collectFormData() {
    // Go through all the form fields and collect their names/values.
    var fd = new FormData();

    $("#uploadForm :input").each(function() {
        var $this = $(this);
        var name  = $this.attr("name");
        var type  = $this.attr("type") || "";
        var value = $this.val();

        // No name = no care.
        if (name === undefined) {
            return;
        }

        // Skip the file upload box for now.
        if (type === "file") {
            return;
        }

        // Checkboxes? Only add their value if they're checked.
        if (type === "checkbox" || type === "radio") {
            if (!$this.is(":checked")) {
                return;
            }
        }

        fd.append(name, value);
    });

    return fd;
}


function handleFiles(files) {
    // Add them to the pending files list.
    for (var i = 0, ie = files.length; i < ie; i++) {
        PENDING_FILES.push(files[i]);
    }
}


function initDropbox() {
    var $dropbox = $("#dropbox");

    // On drag enter...
    $dropbox.on("dragenter", function(e) {
        e.stopPropagation();
        e.preventDefault();
        $(this).addClass("active");
    });

    // On drag over...
    $dropbox.on("dragover", function(e) {
        e.stopPropagation();
        e.preventDefault();
    });

    // On drop...
    $dropbox.on("drop", function(e) {
        e.preventDefault();
        $(this).removeClass("active");

        // Get the files.
        var files = e.originalEvent.dataTransfer.files;
        handleFiles(files);

        // Update the display to acknowledge the number of pending files.
        $dropbox.text(PENDING_FILES.length + " files ready for upload!");
    });

    // If the files are dropped outside of the drop zone, the browser will
    // redirect to show the files in the window. To avoid that we can prevent
    // the 'drop' event on the document.
    function stopDefault(e) {
        e.stopPropagation();
        e.preventDefault();
    }
    $(document).on("dragenter", stopDefault);
    $(document).on("dragover", stopDefault);
    $(document).on("drop", stopDefault);
}
