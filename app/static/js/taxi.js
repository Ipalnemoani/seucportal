var defaultOpts = {
    visiblePages: 10,
    prev: "Prev",
    onPageClick: function(event, page){
        console.log('sdjhvfcjdsavgcavcasdjhvasdjvcga')
        var name = $('#knox-id').val();
        var ticket = $('#ticket-number-admin').val();
        var sdate = $('#start-date.start-date').val();
        var edate = $('#end-date.end-date').val();

        $.get("/taxi/adminpanel", {'page':page, 'name':name, 'ticket':ticket, 'sdate':sdate, 'edate':edate}, function(data)
        {
            var res = JSON.parse(JSON.stringify(data));
            var taxitable = document.getElementById('taxi-tbody');
            //console.log(res)
            if (res.phtml) {
                taxitable.outerHTML = res.phtml;
            }
            $(document).ready(function(){
                $('[data-toggle="tooltip"]').tooltip({animation: true});
            });

            $(document).ready(function(){
                $('[data-toggle="popover"]').popover({container: 'body',
                    html: "true",
                });
            });

        });
    }
};

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip({animation: true});
});



function get_file(name, rowid) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            resp_data = JSON.parse(this.responseText)

            if ( resp_data.content == 'img' ){
                $("#approval-image").attr("src", "data:image/jpg;base64,"+resp_data.btype);
                $('#imageModal').modal('show');
            } else if ( resp_data.content == 'pdf' ) {
                window.open('open_download_file?name='+resp_data.name+"&row="+resp_data.rowid);
            } else if ( resp_data.content == 'mht' || resp_data.content == 'msg' || resp_data.content == 'eml') {
                window.open('open_download_file?name='+resp_data.name+"&row="+resp_data.rowid);
            }
        }
    }
    xhr.open('POST', 'open_download_file', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({name:name, row:rowid}));
}

function edit_request(rowid, page) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            resp_data = JSON.parse(this.responseText)

            var taxitable = document.getElementById('edit-modal-body')
            taxitable.outerHTML = resp_data.phtml
            $('#editTaxiModal').modal('show')
            $('.clockpicker').clockpicker({
                placement: 'bottom',
                align: 'left',
                donetext: 'Done',
                autoclose: 'true'
            });
        }
    }
    xhr.open('GET', 'edit_request?row='+rowid+'&page='+page, true);
    xhr.send();
}

function input_request_approval(button) {
    var buttonid = button.id
    var _validFileExtensions = button.accept;
    var fileName = button.files[0].name;
    var filext = fileName.split('.').pop().toLowerCase();
    if (_validFileExtensions.includes(filext) == false){
        swal("Unsupported file format!", 'Please use one of the supported format   ('+ button.accept+ ')', "error" );
        return false
    }
    if ( fileName.length >= 40 ){
        fileName = fileName.slice(0, 40)+"...";
    }
    $('span[id="'+buttonid+'-label"]')[0].innerText = fileName;
}


$(document).on('click', '.date-trip', function() {
    $(this).datepicker({
        format: 'yyyy-mm-dd',
        todayHighlight: true,
        autoclose: true,
    }).focus();
})

function save_edit_request(){

    var formData = document.getElementById("edit-request-form");
    var formElements = formData.elements;

    var form_data = new FormData();
    for(var i = 0 ; i < formElements.length ; i++){
        var item = formElements.item(i);
        form_data.append(item.name, item.value);
    }

    form_data.append("edit-approval", document.getElementById('edit-approval').files[0]);

    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'edit_request', true);
    xhr.send(form_data);
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            resp_data = JSON.parse(this.responseText)
            if (resp_data.status == 'ok') {
                var taxitable = document.getElementById('taxi-tbody');
                taxitable.outerHTML = resp_data.phtml;
                $('#editTaxiModal').modal('hide');
                $('[data-toggle="popover"]').popover({container: 'body',
                    html: "true",
                });
            }
        }
    }
}

function create_trip_submit(){
    var formData = document.getElementById("create-trip");
    var formElements = formData.elements;

    var form_data = new FormData()
    for(var i = 0 ; i < formElements.length ; i++){
        var item = formElements.item(i);
        form_data.append(item.name, item.value);
    }
}

function get_trip_filter(filtrObj){
    var date_filter = $('#date.search-date').val();
    var filter = filtrObj.value;

    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'taxi?date='+date_filter+'&type='+filter, true);
    xhr.send();
}

function get_filters_data() {
    var searchData = document.getElementsByClassName('search-data');
    var jsonData = {};
    for(var i = 0 ; i < searchData.length ; i++){
        var colname = searchData.item(i).name;
        var item = searchData.item(i).value.trim().toLowerCase();
        jsonData[colname] = item;
    }

    $.get("/taxi/adminpanel", {'page':1,
                              'name':jsonData['knox-id'],
                              'ticket':jsonData['ticket-number-admin'],
                              'sdate':jsonData['start-date'],
                              'edate':jsonData['end-date'],
                              'pagination':1},
                              function(data){
          resp_data = JSON.parse(JSON.stringify(data));
          if (resp_data.status == 'ok') {
              var taxitable = document.getElementById('taxi-tbody');
              taxitable.outerHTML = resp_data.phtml;
              $(document).ready(function(){
                  $('[data-toggle="tooltip"]').tooltip({animation: true});
              });

              $(document).ready(function(){
                  $('[data-toggle="popover"]').popover({container: 'body',
                      html: "true",
                  });
              });

              $('#taxi-pagination').twbsPagination('destroy');
              $('#taxi-pagination').twbsPagination($.extend({}, defaultOpts,
                  {
                      totalPages: resp_data.pqty
                  }));
            }
      });
  };
// };

function removeFilters() {
    $('#knox-id, #ticket-number-admin, .start-date, .end-date').val('');
    $('#remove_filter_button, #apply_filter_button').attr('disabled', 'true');

    $.get("/taxi/adminpanel", {'page':1,
                              'name':'',
                              'ticket':'',
                              'sdate':'',
                              'edate':'',
                              'pagination':1},
                              function(data){
          resp_data = JSON.parse(JSON.stringify(data));
          //console.log(resp_data)
          if (resp_data.status == 'ok') {
              var taxitable = document.getElementById('taxi-tbody');
              taxitable.outerHTML = resp_data.phtml;
              $(document).ready(function(){
                  $('[data-toggle="tooltip"]').tooltip({animation: true});
              });

              $(document).ready(function(){
                  $('[data-toggle="popover"]').popover({container: 'body',
                      html: "true",
                  });
              });

              $('#taxi-pagination').twbsPagination('destroy');
              $('#taxi-pagination').twbsPagination($.extend({}, defaultOpts,
                  {
                      totalPages: resp_data.pqty
                  }));
            }
      });
  }

function editConfirm(inputid, buttonid, rowid){

    var newinput = document.getElementById(inputid);
    var newbutton = document.getElementById("fas-"+rowid);

    newbutton.innerHTML = newinput.value;
    var emailbtn = $('#email-'+rowid);

    if (newinput.value != '') {

        emailbtn.removeAttr('disabled');
        emailbtn.attr('onClick', 'notifyEmail('+rowid+')');
        emailbtn.attr('title', 'Send Email Notify to Employee');
        emailbtn.tooltip('fixTitle');
    } else {
        emailbtn.attr('disabled', 'true');
        emailbtn.attr('title', 'Note is empty! To send email, please, add Note!');
        emailbtn.tooltip('fixTitle');

    }

    $('#'+buttonid).dropdown('toggle');

    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'addnote', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({rowid:rowid, note:newinput.value}));
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            resp_data = JSON.parse(this.responseText);
        }
    }
}

function change_status(rowid, stat) {
    $.get("/taxi/changestatus", {'rowid':rowid, 'stat':stat}, function(data)
        {
            var res = JSON.parse(JSON.stringify(data));
            if ( res.status == 'ok' ) {
                var bname = $('#status-btn-'+rowid);
                var iname = $('#status-i-'+rowid);
                var emailbtn = $('#email-'+rowid);
                var drdnote = $('#dropdown-note-'+rowid);
                var noteinput = $('#fas-'+rowid);
                var editinput = $('#edit-input-'+rowid);

                if (stat == 1) {
                    drdnote.attr('style', 'height: 22px; visibility: hidden;');

                    bname.attr('style', 'color:seagreen; background-color: #fff; border-color: #fff;');
                    bname.attr('title', 'Trip was Confirmed!');
                    bname.attr('onClick', "change_status("+rowid+", 0)");

                    iname.attr('class', 'fas fa-clipboard-check');
                    iname[0].innerHTML = " Confirm";
                    noteinput[0].innerHTML = "";
                    editinput[0].value = "";

                    emailbtn.attr('disabled', 'true');
                    emailbtn.attr('title', 'Trip was Confirmed! Sending Email   Not Possible!');

                } else if ( stat == 0 ) {
                    drdnote.attr('style', 'height: 22px; visibility: visible;');
                    bname.attr('style', 'color:#ffb802; background-color: #fff; border-color: #fff;');
                    bname.attr('title', 'Trip Confirmation in Progress!');
                    bname.attr('onClick', "change_status("+rowid+", 1)");
                    iname.attr('class', 'fas fa-tasks');
                    iname[0].innerHTML = " In Progress";
                    emailbtn.attr('title', 'Note is empty! To send email, please, add Note!');
                }

                emailbtn.tooltip('fixTitle');
            }
        });
}

function notifyEmail(rowid) {
    var note = $('#edit-button-'+rowid)
    $.get("/sendmail", {'rowid':rowid, 'module':'taxi'}, function(data) {
        var res = JSON.parse(JSON.stringify(data));
    });
}

$(document).on('click', '#download_filter_button', function() {
    var searchData = document.getElementsByClassName('search-data');
    var jsonData = {};
    for(var i = 0 ; i < searchData.length ; i++){
        var colname = searchData.item(i).name;
        var item = searchData.item(i).value.trim().toLowerCase();
        jsonData[colname] = item;
    }

    this.href = 'adminpanel/file?name='+jsonData['knox-id']+'&ticket='+jsonData['ticket-number-admin']+'&sdate='+jsonData['start-date']+'&edate='+jsonData['end-date'];
});

$(document).on('click', '#statistic_filter_button', function() {

    var searchData = document.getElementsByClassName('search-data');
    //console.log(searchData)
    var jsonData = {};
    for(var i = 0 ; i < searchData.length ; i++){
        var colname = searchData.item(i).name;
        //console.log(searchData.item(i).value)
        var item = searchData.item(i).value.trim().toLowerCase();
        jsonData[colname] = item;
    }

    if ( jsonData['start-date'] == '' && jsonData['end-date'] == '') {
        swal({
            icon: "warning",
            title: "Warning",
            text: "To Get Statistics, Please, Select Period!",
          });
        return
    } else if (jsonData['start-date'] == '' && jsonData['end-date'] != ''){
        swal({
            icon: "warning",
            title: "Warning",
            text: "To Get Statistics, Please, Select Start Period Date!",
          });
    } else if (jsonData['start-date'] != '' && jsonData['end-date'] == ''){
        swal({
            icon: "warning",
            title: "Warning",
            text: "To Get Statistics, Please, Select End Period Date!",
          });
    } else {

        $.get("/taxi/statistic", {'module':'taxi', 'knoxid':jsonData['knox-id'], 'sdate':jsonData['start-date'], 'edate':jsonData['end-date']}, function(data) {
            var res = JSON.parse(JSON.stringify(data));
            var statmodal = document.getElementById('modal-stat-content-div');
            console.log(statmodal)
            statmodal.outerHTML = res.phtml;
            $('#statisticModal').modal('show');
        });
    }

});

$(document).on('click', '.approval-btn', function (event){
    get_file($(this).attr('name'), $(this).attr('data-row'))
});
