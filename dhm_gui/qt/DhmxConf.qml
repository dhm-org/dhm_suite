import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Extras 1.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.0

MouseArea {
    signal pack_cmd(string cmd)
    id: dhmx_config
    visible: true
    width: 700
    height: 600
    drag.target: dhmx_config
    transformOrigin: Item.TopLeft

    property variant clickX: 1
    property variant delta: 0




    Rectangle {
        id: drag_area
        anchors.fill: parent
        color: "#c1bebe"
        border.color: "#242424"
        border.width: 4
    }

    /* Scaling handle */
    Button{
        id: button_resize
        x: 667
        y: 567
        width: 25
        height :25
        display: AbstractButton.IconOnly
        icon.source: "images/ui_handle.png"

        MouseArea{
            anchors.fill: parent
            property var cur_mouse_pos
            property var prev_mouse_pos_x: 0
            onPressed: {
                cur_mouse_pos = mouse.x
            }

            onPositionChanged: {
                cur_mouse_pos = mouse.x
                cur_mouse_pos = cur_mouse_pos - prev_mouse_pos_x
                prev_mouse_pos_x = mouse.x
                dhmx_config.scale += cur_mouse_pos / 1024
            }
        }
    }

    Button {
        id: button_save
        objectName: "button_save"
        x: 126
        y: 537
        text: qsTr("Save to File")

        onClicked: {
            pack_cmd('session name='+textField_session_name.text+',description='+textArea_desc.text+',wavelength=['+send_wl()+'],dx='+metric_conversion((spinBox_t3_dx.realValue),"um","m")+',dy='+metric_conversion((spinBox_t3_dy.realValue),"um","m")+',crop_fraction='+(spinBox_t2_crop.realValue)+',rebin_factor='+(spinBox_t2_rebin.value)+',focal_length='+metric_conversion((spinBox_t4_focal.realValue),"mm","m")+',numerical_aperture='+metric_conversion((spinBox_t4_num_ap.realValue),"mm","m")+',system_magnification='+metric_conversion((spinBox_t4_sys_mag.realValue),"mm","m"))
        }
    }

    Button {
        signal qml_signal_close
        objectName: "button_close"
        id: button_close
        x: 552
        y: 537
        text: qsTr("Close")

        onClicked: {
            dhmx_config.visible = false
            qml_signal_close()
        }
    }

    Label {
        id: label_filename
        x: 29
        y: 99
        text: qsTr("Name")
    }

    TextField {
        id: textField_session_name
        objectName: "textField_session_name"
        x: 117
        y: 87
        width: 535
        height: 40
        text: qsTr("")
        placeholderText: "Please input a session name"
    }

    Button {
        id: button_load
        objectName: "button_load"
        x: 17
        y: 537
        text: qsTr("Load From File")
    }

    Label {
        id: label_desc
        x: 17
        y: 141
        width: 80
        height: 16
        text: qsTr("Description")
    }

    TextArea {
        background: Rectangle{
            anchors.fill: parent
            color:"white"
        }

        id: textArea_desc
        objectName: "textArea_desc"
        x: 119
        y: 141
        width: 533
        height: 81
        text: qsTr("")
        placeholderText: "Please input a description"
    }

    TabBar{
        id: bar
        x: 17
        y: 251
        width: 661
        height: 260
        currentIndex: 0

        TabButton{
            text: qsTr("Light Source Parameters")//t1
        }
        TabButton{
            text: qsTr("Image Settings")//t3
        }
        TabButton{
            text: qsTr("Hologram Parameters")//t2
        }
        TabButton{
            text: qsTr("Lens Information")//t4
        }
    }

    StackLayout{
        x: -22
        y: -280
        currentIndex: bar.currentIndex

        Item{
            id: tab1

            RadioDelegate {
                id: radio_t1_mono
                objectName: "radio_t1_mono"
                x: 150
                y: 622
                text: qsTr("Monochromatic")
                onClicked: {
                    update_combo()
                    update_wl()
                }
                onCheckedChanged:  {
                    update_combo()
                    update_wl()
                }
            }

            RadioDelegate {
                id: radio_t1_multi
                objectName: "radio_t1_multi"
                x: 139
                y: 671
                text: qsTr("Multi wavelength")
                onClicked: {
                    update_combo()
                    update_wl()
                }
                onCheckedChanged: {
                    update_combo()
                    update_wl()
                }
            }


            ComboBox {
                id: combo_t1_w1
                objectName: "combo_t1_w1"
                x: 394
                y: 607
                width: 178
                height: 40
                flat: false
                model: ListModel{
                    id: model_w1
                    objectName: "model_w1"
                    ListElement{
                        text: "405"
                    }
                    ListElement{
                        text: "488"
                    }
                    ListElement{
                        text: "532"
                    }
                }
            }

            ComboBox {
                id: combo_t1_w2
                objectName: "combo_t1_w2"
                x: 394
                y: 653
                width: 178
                height: 40
                model: ListModel{
                    id: model_w2
                    ListElement{
                        text: "405"
                    }
                    ListElement{
                        text: "488"
                    }
                    ListElement{
                        text: "532"
                    }
                }
            }

            ComboBox {
                id: combo_t1_w3
                objectName: "combo_t1_w3"
                x: 394
                y: 699
                width: 178
                height: 40
                model: ListModel{
                    id: model_w3
                    ListElement{
                        text: "405"
                    }
                    ListElement{
                        text: "488"
                    }
                    ListElement{
                        text: "532"
                    }
                }
            }

            Label {
                id: label_t1_nm_001
                x: 591
                y: 622
                text: qsTr("nm")
            }

            Label {
                id: label_t1_nm_1
                x: 591
                y: 671
                text: qsTr("nm")
            }

            Label {
                id: label_t1_nm_2
                x: 591
                y: 711
                text: qsTr("nm")
            }

        }
        Item{
            id: tab3

            Label {
                id: label_t3_um_y
                x: 616
                y: 690
                width: 26
                height: 17
                text: qsTr("µm")
            }

            Label {
                id: label_t3_um_x
                x: 616
                y: 634
                width: 26
                height: 17
                text: qsTr("µm")
            }

            DoubleSpinBox {
                id: spinBox_t3_dy
                objectName: "spinBox_t3_dy"
                decimals: 3
                editable: true
                x: 470
                y: 678
                width: 140
                height: 40
                //stepSize: 0
            }

            Label {
                id: label_t3_pixel_y
                x: 381
                y: 690
                width: 86
                height: 17
                text: qsTr("Pixel Pitch y")
            }

            DoubleSpinBox {
                id: spinBox_t3_dx
                decimals: 3
                editable: true
                objectName: "spinBox_t3_dx"
                x: 470
                y: 622
                //stepSize: 0
            }

            Label {
                id: label_t3_pixel_x
                x: 381
                y: 634
                width: 86
                height: 17
                text: qsTr("Pixel Pitch x")
            }

            SpinBox {
                id: spinBox_t3_height
                objectName: "spinBox_t3_height"
                x: 151
                y: 678
                editable: true
                value: 2048
                from: 0
                to: 99999
            }

            Label {
                id: label_t3_height
                x: 83
                y: 690
                text: qsTr("Height")

            }

            Label {
                id: label_t3_width
                x: 88
                y: 634
                width: 41
                height: 17
                text: qsTr("Width")
            }

            SpinBox {
                id: spinBox_t3_width
                objectName: "spinBox_t3_width"
                x: 151
                y: 622
                editable: true
                value: 2048
                from: 0
                to: 99999
            }

            Label {
                id: label_t3_px
                x: 297
                y: 634
                width: 41
                height: 17
                text: qsTr("px")
            }

            Label {
                id: label_t3_px1
                x: 297
                y: 684
                width: 41
                height: 17
                text: qsTr("px")
            }

        }

        Item{
            id: tab2

            DoubleSpinBox {
                id: spinBox_t2_crop
                objectName: "spinBox_t2_crop"
                x: 348
                y: 676
            }

            SpinBox {
                id: spinBox_t2_rebin
                objectName: "spinBox_t2_rebin"
                x: 348
                y: 619
                editable: true
            }

            Label {
                id: label_t2_rebin
                x: 219
                y: 630
                text: qsTr("Rebin Factor")
            }

            Label {
                id: label_t2_crop
                x: 212
                y: 687
                text: qsTr("Crop Fraction")
            }
        }
        Item{
            id: tab4

            DoubleSpinBox {
                id: spinBox_t4_focal
                objectName: "spinBox_t4_focal"
                x: 333
                y: 597
                editable: true
                realFrom: 1.00
                realTo: 20.00
            }

            Label {
                id: label_t4_focal
                x: 203
                y: 608
                text: qsTr("Focal Length")
            }

            Label {
                id: label2
                x: 479
                y: 609
                text: qsTr("mm")
            }

            DoubleSpinBox {
                id: spinBox_t4_num_ap
                objectName: "spinBox_t4_num_ap"
                x: 333
                y: 671
                editable: true
                realFrom: 0.1
                realTo: 1.0
            }

            Label {
                id: label_t4_num_ap
                x: 156
                y: 683
                text: qsTr("Numerical Aperture")
            }

            DoubleSpinBox {
                id: spinBox_t4_sys_mag
                objectName: "spinBox_t4_sys_mag"
                x: 333
                y: 721
                editable: true
                realFrom: 1.00
                realTo: 200.00
            }

            Label {
                id: label_t4_sys_mag
                x: 144
                y: 733
                text: qsTr("System Magnification")
            }
        }

    }

    Label {
        id: label
        x: 17
        y: 37
        text: qsTr("Session Parameters")
        font.bold: false
        font.pointSize: 18
    }

    FileDialog{
        signal qml_signal_send_file_path(string path, string cmd)
        id: dhmx_fd
        objectName: "dhmx_fd"
        title: "DEFAULT"
        //folder: shortcuts.home
        nameFilters: ["Image files (*.tif *.bmp *.png *.jpg)","All files (*)"]

        property string cmd_type: ""

        onAccepted: {
            var path = dhmx_fd.fileUrl.toString();
            var cleanPath
            path = path.replace(/^(file:\/{2})/,"");
            cleanPath = decodeURIComponent(path);
            //pack_cmd(cmd_type+cleanPath)

            //Specific just for this window
            //UPDATE: Do not update the session name field with a path
            //textField_session_name.text = cleanPath

        }
        onRejected: {
            dhmx_fd.close()
        }
        Component.onCompleted: visible = false
    }

    Button {
        id: button_apply
        x: 235
        y: 537
        text: qsTr("Apply")
        objectName: "button_apply"
        onClicked: {
            pack_cmd('session name='+textField_session_name.text+',description='+textArea_desc.text+',wavelength=['+send_wl()+'],dx='+metric_conversion((spinBox_t3_dx.realValue),"um","m")+',dy='+metric_conversion((spinBox_t3_dy.realValue),"um","m")+',crop_fraction='+(spinBox_t2_crop.realValue)+',rebin_factor='+(spinBox_t2_rebin.value)+',focal_length='+metric_conversion((spinBox_t4_focal.realValue),"mm","m")+',numerical_aperture='+metric_conversion((spinBox_t4_num_ap.realValue),"mm","m")+',system_magnification='+metric_conversion((spinBox_t4_sys_mag.realValue),"mm","m"))
        }
    }


    /* Update fields as soon as the window is opened */
    onVisibleChanged: {
        //  onActiveChanged: {
        update_wl()
    }


    /* Functions to change visibility and sensitivity of fields */
    function update_wl(){
        if(radio_t1_mono.checked){
            combo_t1_w1.enabled = true
            combo_t1_w2.enabled = false
            combo_t1_w3.enabled = false
        }
        else if(radio_t1_multi.checked){
            combo_t1_w1.enabled = true
            combo_t1_w2.enabled = true
            combo_t1_w3.enabled = true
        }
        else{
            combo_t1_w1.enabled = false
            combo_t1_w2.enabled = false
            combo_t1_w3.enabled = false
        }
    }
    function update_combo(){
        if(radio_t1_mono.checked){
            radio_t1_multi.checked = false
        }
        if(radio_t1_multi.checked){
            radio_t1_mono.checked = false
        }
    }
    function send_wl(){
        if(radio_t1_mono.checked){
           // return model_w1.get(combo_t1_w1.currentIndex).text
            return metric_conversion(model_w1.get(combo_t1_w1.currentIndex).text,"nm","m")
        }
        if(radio_t1_multi.checked){
            //return model_w1.get(combo_t1_w1.currentIndex).text+","+model_w2.get(combo_t1_w2.currentIndex).text+","+model_w3.get(combo_t1_w3.currentIndex).text
            return metric_conversion(model_w1.get(combo_t1_w1.currentIndex).text,"nm","m")+","+metric_conversion(model_w2.get(combo_t1_w2.currentIndex).text,"nm","m")+","+metric_conversion(model_w3.get(combo_t1_w3.currentIndex).text,"nm","m")
        }
    }
    function metric_conversion(item, scale_in, scale_out){
        var scale_factor = 0
       // var item_output = parseInt(item,10)
        var item_output = item

        if(scale_in == "nm" && scale_out == "m"){
            scale_factor = 1e-9
        }
        if(scale_in == "um" && scale_out == "m"){
            scale_factor = 1e-6
        }
        if(scale_in == "mm" && scale_out == "m"){
            scale_factor = 1e-2
        }

        if(scale_in == "m" && scale_out == "mm"){
            scale_factor = 1e2
        }
        if(scale_in == "m" && scale_out == "um"){
            scale_factor = 1e6
        }
        if(scale_in = "m" && scale_out == "nm"){
            scale_factor = 1e9
        }
        return (item_output * scale_factor).toPrecision(6)
    }

    function convert_to_bytes(input_str){
        var str = input_str;
        var bytes = []; // char codes
        var bytesv2 = []; // char codes

        for (var i = 0; i < str.length; ++i) {
          var code = str.charCodeAt(i);

          bytes = bytes.concat([code]);

          bytesv2 = bytesv2.concat([code & 0xff, code / 256 >>> 0]);
        }

        // 72, 101, 108, 108, 111, 31452
        console.log('bytes', bytes.join(', '));

        // 72, 0, 101, 0, 108, 0, 108, 0, 111, 0, 220, 122
        console.log('bytesv2', bytesv2.join(', '));

        return bytesv2
    }

    /* For writing a session configuration (.ses) file */
    function get_session_cfg(){
        return ('session name='+textField_session_name.text+',description='+textArea_desc.text+',wavelength=['+send_wl()+']\n,dx='+metric_conversion((spinBox_t3_dx.realValue),"um","m")+'\n,dy='+metric_conversion((spinBox_t3_dy.realValue),"um","m")+'\n,crop_fraction='+(spinBox_t2_crop.realValue)+'\n,rebin_factor='+(spinBox_t2_rebin.value)+'\n,focal_length='+metric_conversion((spinBox_t4_focal.realValue),"mm","m")+'\n,numerical_aperture='+metric_conversion((spinBox_t4_num_ap.realValue),"mm","m")+'\n,system_magnification='+metric_conversion((spinBox_t4_sys_mag.realValue),"mm","m"))
    }
}

