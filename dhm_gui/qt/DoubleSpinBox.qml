import QtQuick 2.3

import QtQuick.Controls 2.1

//Item {
//    property int decimals: 2
//    property real realValue: 0.0
//    property real realFrom: 0.0
//    property real realTo: 100.0
//    property real realStepSize: 1.0
//    property bool realEdit: true

    SpinBox{
        property int decimals: 2
        property real realValue: value / 100
        property real realFrom: 0.0
        property real realTo: 100.0
        property real realStepSize: 0.25
        property bool realEdit: true
        property real factor: Math.pow(10, decimals)
        id: spinbox
        editable: realEdit
        stepSize: realStepSize*factor
        value: realValue*factor
        //value: 0
        to : realTo*factor
        from : realFrom*factor
        validator: DoubleValidator {
            bottom: Math.min(spinbox.from, spinbox.to)*spinbox.factor
            top:  Math.max(spinbox.from, spinbox.to)*spinbox.factor
        }

        textFromValue: function(value, locale) {
            //realValue = parseFloat(value*1.0/factor).toFixed(decimals);
            //return parseFloat(value*1.0/factor).toFixed(decimals);
            realValue = Number(value/factor).toLocaleString(locale, 'f', spinbox.decimals)
            return Number(value/factor).toLocaleString(locale, 'f', spinbox.decimals)
        }
        valueFromText: function(text, locale) {
            //realValue = Number.fromLocaleString(locale, text) * 100
            value = Number.fromLocaleString(locale, text) * factor
            return Number.fromLocaleString(locale, text) * factor
        }

    }
//}
