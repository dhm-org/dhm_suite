import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Extras 1.4
import QtQuick.Layouts 1.3


MouseArea {
    id: dhmx_cmd
    objectName: "cmd_win"

    visible: true
    width: 650
    height: 460
    drag.target: dhmx_cmd

    signal click_run()
    signal row_added()

    property int cmd_index: 0
    property int cmd_max: 0
    property int max_size: 150
    property bool last_is_curr_selected: false
    property color color_blue_dhmx: "#3C77D4"
    property color color_transparent: "#00000000"
    property color color_background: "#dddae0"
    property color color_button_border: "#c7cbf4"

    Rectangle {
        id: bg
        height: 900
        anchors.fill: parent
        color: "#c1bebe"
        border.color: "#242424"
        border.width: 4
    }



    /* Command Window List component */
    /* Each list item will have a string, text color, highlight and type */

    Component {
        id: cmd_delegate

        Item {
            width: cmd_list.width - 3 // a slight offset so that the text does not reaach the absolute edge of the box and cause a visual tangent
            height: cmd_text_element.height
            objectName: cmd_type
            x: 3 // a slight offset so that the text does not reaach the absolute edge of the box and cause a visual tangent

            /* Highlight (turned off) */
            Rectangle{
                id: cmd_bg
                anchors.fill:parent
                color: cmd_highlight
            }

            /* text component*/
            TextEdit {
                id: cmd_text_element
                width: cmd_list.width - 3 // a slight offset so that the text does not reaach the absolute edge of the box and cause a visual tangent
                readOnly: true
                text: cmd_str
                color: cmd_color
                //textFormat: Text.RichText
                font.pixelSize: 16
                wrapMode: Text.WordWrap
                font.bold:false
            }
            Component.onCompleted: {
                cmd_list.positionViewAtEnd()
            }

            /* Highlighting features here */
            MouseArea{
                id: test
                anchors.fill:parent
                hoverEnabled: true
                onClicked: {
                    //select text
                    if(parent.objectName == "1")
                       text_cmd_edit.text = cmd_text_element.text
                }
                onEntered: {
                    //highlight
                    if(parent.objectName == "1"){
                        cmd_index = index
                        set_index_highlight("mouse")

                    }
                }
                onExited: {
                    //remove highlight
                    if(parent.objectName == "1"){
                        clear_last_selection()
                    }
                }
            }
        }
    }

    ScrollView {
        id: cmd_scroll_view
        x: 23//23
        y: 62
        width: 605
        height: 270//274
        // highlightOnFocus: true

//        Rectangle {
//            color:"white"
//            anchors.fill: parent
//        }
        ListView {
            id: cmd_list
            snapMode: ListView.SnapOneItem
            boundsBehavior: Flickable.StopAtBounds
            //x: 5
            anchors.fill: parent
            model: cmd_model
            delegate: cmd_delegate
            cacheBuffer: 999

            Rectangle {
                y: -8
                color:color_background
                width:cmd_scroll_view.width
                height: cmd_scroll_view.height + 14
                z: -1
            }
            Flickable{
                id: flicking
                anchors.fill: parent

            }
        }


    }

    ListModel {
        id: cmd_model
        objectName: "cmd_model"
        ListElement {
            cmd_str: "Awaiting for responses..."
            cmd_color: "Gray"  /* Gray because it's not a response or command */
            cmd_highlight:"transparent"
            cmd_type: "0"
        }

        /* QML Slot */
        function py_sig_append_cmd_list(cmd_str, cmd_color, cmd_highlight, cmd_type){
            clear_last_selection()
            update_list()

            /* Set scrollback limit */
            var row_total = cmd_model.rowCount()
            var temp
            if(row_total > max_size){
                for(var i = 0; i < row_total; i++){

                    /* If its the first element, skip it, it will be overwritten */
                    /* It will 'pop' (overwrite) off the queue */
                    if(i == 0){
                        continue;
                    }

                    temp = cmd_model.get(i)
                    cmd_model.set(i-1,temp)
                }
            }
            /* End scrollback limit check */

            if (row_total > max_size)
               cmd_model.set(max_size,{cmd_str: cmd_str, cmd_color: cmd_color, cmd_highlight: cmd_highlight, cmd_type: cmd_type})

            else
               cmd_model.append({cmd_str: cmd_str, cmd_color: cmd_color, cmd_highlight: cmd_highlight, cmd_type: cmd_type})

            text_cmd_edit.focus = true
        }

    }

    Button {
        id: button_close
        x: 551
        y:409
        width: 77
        height: 30
        text: qsTr("Close")
        onClicked: {
            dhmx_cmd.visible = false
        }
    }

    Button {
        id: button_apply
        x: 23
        y: 409
        width: 75
        height: 30
        text: qsTr("Apply")
        onClicked:{
            add_and_send_cmd()
        }
    }

    Label {
        id: label
        x: 24
        y: 20
        text: qsTr("Manual Command")
        font.pointSize: 18
    }

    Text {
        id: tag_enter_cmd
        x: 23
        y: 342
        text: qsTr("Enter Command:")
        font.bold: true
        font.pointSize: 12
    }

    TextField {
        id: text_cmd_edit
        x: 23
        objectName: "text_cmd_edit"
        y: 360
        width: 605
        height: 27
        inputMask: qsTr("")
        // echoMode: 0
        font.pointSize: 10
        layer.enabled: enabled
        focus: true
        maximumLength: 255 /* No message can be longer than 256 bytes */


        //Placeholder text is dynamic and will dissapear after first input
        placeholderText: qsTr("Enter command here...")
        onTextChanged:  {
            text_cmd_edit.placeholderText = ""
        }
        onFontChanged: {
            text_cmd_edit.focus = true
        }
        Keys.onReturnPressed:{
            add_and_send_cmd()
        }
        Keys.onUpPressed: scan_list("up")
        Keys.onDownPressed: scan_list("down")
    }

    /* Simple function to just update the command window with a command string, this is only used for other
     * windows calling the command window to update */
    function add_cmd(cmd_string){
           cmd_model.py_sig_append_cmd_list(cmd_string,"steelblue","transparent","1")
    }

    /* Directly adds the user's command to the list and sends the command to be processed by python */
    function add_and_send_cmd(){
        if(text_cmd_edit.text != ""){
           cmd_model.py_sig_append_cmd_list(text_cmd_edit.text,"steelblue","transparent","1")

           /* Send QML Signal to Python */
           click_run()
           text_cmd_edit.text=""
        }
    }

    /* Updates the scroll view size and determines if/when to use a scrollbar */
    function update_scroll_view(){
        if(cmd_scroll_view.contentHeight >= cmd_scroll_view.height && cmd_scroll_view.contentHeight != -1){
           // console.log("Updating height. Height is: ",cmd_scroll_view.contentHeight)
           flicking.contentY = cmd_scroll_view.contentHeight
        }
    }

    /* Updates the list object index and maximum list size with each entry */
    function update_list(){
        cmd_max = cmd_list.count
        if(cmd_max > max_size)
            cmd_max = max_size
        cmd_index = cmd_max
        cmd_list.currentIndex = cmd_index
    }

    /* This scans the list of objects and highlights the active list entry */
    function scan_list(dir){
        var get_cmd
        if(dir === "up" && cmd_index >= 0) {
            search_index(dir)
        }
        if(dir === "down" && cmd_index <=  cmd_max) {
            search_index(dir)
        }
        clear_all_unselected()
    }

    /* This function sets the highlighted background of the current list item */
    function set_index_highlight(ctrl){
        var get_cmd
        get_cmd = cmd_model.get(cmd_index)
        get_cmd.cmd_highlight = "steelblue"
        get_cmd.cmd_color = "white"
        if(ctrl != "mouse")
        text_cmd_edit.text = get_cmd.cmd_str
        cmd_list.currentIndex = cmd_index
    }

    /* Upon hitting the return key, clear the selection */
    function clear_last_selection(){
        var get_cmd
        get_cmd = cmd_model.get(cmd_index)

        get_cmd.cmd_highlight = "transparent"


        /* Check if last command in list was a command, if so, return back to command color from highlight */
        if(get_cmd.cmd_type === "1")
           get_cmd.cmd_color = "steelblue"
    }

    /* This function will clear all highlighted backgrounds other than the currently selected item */
    function clear_all_unselected() {
        var get_cmd
        for(var i = 0; i <= cmd_max; i++){
            get_cmd = cmd_model.get(i)

            if(i != cmd_index)
                get_cmd.cmd_highlight = "transparent"
        }
    }

    function search_index(dir){
        var get_cmd
        var start_index
        start_index = cmd_index
        /* Search up the list for the next nearest user command */
        if(dir === "up") {
            for(var i = cmd_index; i >= 0; i--){
                get_cmd = cmd_model.get(i)

                /* "1" means it is a user command, any other number can be reserved for responses */
                if(get_cmd.cmd_type === "1"){
                    /* If the start_index is the same as i, that means it is the current command that is selected
                     * Therefore skip it and move to the next available */
                    /* There is a flag in place to indentify if the last item is a command, this occurs when there
                     * is no response from the CMD server, so the user will be able to accept the last command */
                    if(start_index == i){
                        if(last_is_curr_selected == true){
                           cmd_index = i
                           set_index_highlight()
                           last_is_curr_selected = false
                           return
                        }
                        else{
                           /* Special case - if we reach the beginning of the list - stay highlighted */
                           if(start_index == 1){
                               set_index_highlight()
                           }
                           /* Otherwise, set font color back to normal command color */
                           else{
                               get_cmd.cmd_color = "steelblue"
                           }
                           continue
                        }
                    }
                    else {
                        cmd_index = i
                        set_index_highlight()
                        return
                    }
                }
            }
        }

        /* Search down the list for the next nearest user command */
        if(dir === "down"){
            for(var i = cmd_index; i <= cmd_max; i++){
                get_cmd = cmd_model.get(i)

                 /* "1" means it is a user command, any other number can be reserved for responses */
                if(get_cmd.cmd_type === "1"){

                    /* If the start_index is the same as i, that means it is the current command that is selected
                     * Therefore skip it and move to the next available */
                    if(start_index == i){
                         get_cmd.cmd_color = "steelblue"
                        continue
                    }
                    else{
                        cmd_index = i
                        set_index_highlight()
                        return
                    }
                }
            }
            /* If nothing is found at the bottom of the list, clear it */
            text_cmd_edit.text = ""
            clear_last_selection()
            last_is_curr_selected = true
        }
    }



}










/*##^## Designer {
    D{i:6;anchors_height:274;anchors_width:605;anchors_x:23;anchors_y:39}
}
 ##^##*/
