$(document).ready(function () {
    var action = { bot_name:"DEFAULT", action_name:"DEFAULT_ACTION", method:"DEFAULT", action:"configure_bot" };

    let req = {
        action: 'get_bots'
    };
    let botsContent = $('#bots-content');

    $.ajax({
        type: "POST",
        beforeSend: function(request) {
            request.setRequestHeader('Content-Type', 'application/json');
        },
        url: "/api/config",
        data: JSON.stringify(req),
        processData: false,
        success: function(data) {
            console.log(data);
            data = JSON.parse(data);

            if (data.error) {
                botsContent.html("<p style='margin: 1rem 2rem'>No bots configured. You can a bot by adding an app and then adding a bot.</p>")
            } else {
                let bots = data.bots;
                let sz = bots.length;
                let table_html = '';

                for (let i = 0; i < sz; i++) {
                    let tableControls = `
                    <td>
                        <div class="field is-grouped is-grouped-right">
                            <p class="control">
                                <a class="button add-bot-btn" id="${bots[i].bot_name}">
                                    Configure Bot
                                 </a>
                            </p>
                        </div>
                    </td>`;
                    table_html += `<tr><td width="5%"><i class="fas fa-user"></i></td><td>${bots[i].bot_name} (${bots[i].app_name})</td>${tableControls}</tr>`
                }
                $('#bots-table-body').html(table_html);

                $('.add-bot-btn').click(function(){
                    action.bot_name = $(this).attr('id');
                    $('#configuration1-modal').addClass('is-active');
                });
            }
        }
    });

    $('#checkbox-reply').click(function() {
        $(".replybox").toggle(this.checked);
    });

    $('#configuration1-next').click(function() {
        $('#configuration2-modal').addClass('is-active');
        $('#configuration1-modal').removeClass('is-active');
    });

    function debugging(){
        console.log(JSON.stringify(action));
    }

    $("#configuration2-next").click(function(){
        if(action.actions) delete action.actions;
        action.method = $('#source option:selected').val();

        action.actions = new Array();

        let cAction = {};

        if(action.method=="react_to_my_mentions" ||
            action.method=="react_to_my_timeline"){
            if($('#text-tags option:selected').val()=="exactly"){
                cAction["exactly"] = $("#filtertext").val();
            }else if($('#text-tags option:selected').val()=="tags"){
                let tagsplit = $("#filtertext").val().split(" ");
                cAction["tags"] = tagsplit;
            }

            let checkbox = new Array();

            if($("#checkbox-reply").is(':checked')){
                checkbox.push($("#checkbox-reply").val());
            }
            if($("#checkbox-favor").is(':checked')){
                checkbox.push($("#checkbox-favor").val());
            }
            if($("#checkbox-follow").is(':checked')){
                checkbox.push($("#checkbox-follow").val());
            }

            if(checkbox.length==1){
                checkbox = checkbox[0];
            }

            cAction["action"] = checkbox;

            if($("#checkbox-reply").is(':checked')){
                cAction["text"] = $("#replytext").val();
            }
        }

        action.actions.push(cAction);

        debugging();

        $.ajax({
            type: "POST",
            beforeSend: function (request) {
                request.setRequestHeader('Content-Type', 'application/json');
            },
            url: "/api/config",
            data: JSON.stringify(req),
            processData: false,
            success: function (data) {
                console.log(data);
                data = JSON.parse(data);
                alter("Action performed");
            }
        });


    });

    $('.delete').click(function() {
        $('.modal').removeClass('is-active');
    });

    $('configuration-modal-close').click(function() {
        $('.modal').removeClass('is-active');
    });



});