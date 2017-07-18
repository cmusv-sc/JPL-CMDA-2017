$(function () {
    var checked_ids;
    $('#jstree_div')
        .jstree({
            'core': {
                'data': {
                    'url': '/climate/keywordTree/', // the URL to fetch the data. Use relative url if required}
                    'data': function (node) {
                        return { 'id': node.id };
                    }
                }
            },
            "checkbox": {
                "keep_selected_style": false
            },
            "state": {
                "key": "keyword_tree"
            },
            "plugins": [ "checkbox", "state"]
        })
        .on('changed.jstree', function (e, data) {
            var checked_texts = [];
//            var selected = $('#jstree_div').jstree(true).get_selected(true)
//                .each (function () {
//                checked_texts.push(this.text);
//            });
            console.log(checked_texts);
        });


//built in filter of tree (search plugin)
    var to = false;
    $('#jstree_div_q').keyup(function () {
        if (to) {
            clearTimeout(to);
        }
        to = setTimeout(function () {
            var v = $('#jstree_div_q').val();
            $('#jstree_div').jstree(true).search(v);
        }, 250);
    });

    $('#submit').click(function () {
        var data = $("#jstree_div").jstree(true).get_checked(true);
        var json = JSON.stringify(data);
        console.log(json);
        $.ajax({
            type: "POST",
            url: "/climate/recommendation/selectedKeywordSearch",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function(){
                location.reload();
            }
        });
    });
});

