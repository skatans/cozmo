#!/usr/bin/env python3

# Copyright (c) 2016 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Modifications by Tuisku Polvinen and Adam Bengtsson 2023

'''The html and javascript for the web page for controlling cozmo'''
html = '''
    <html>
        <head>
            <title>remote_control_cozmo.py display</title>
        </head>
        <body>
            <h1>Remote Control Cozmo</h1>
            <table>
                <tr>
                    <td valign = top>
                        <div id="cozmoImageMicrosoftWarning" style="display: none;color: #ff9900; text-align: center;">Video feed performance is better in Chrome or Firefox due to mjpeg limitations in this browser</div>
                        <img src="cozmoImage" id="cozmoImageId" width=640 height=480>
                        <div id="DebugInfoId"></div>
                    </td>
                    <td width=30></td>
                    <td valign=top>
                        <h2>Controls:</h2>

                        <b>R F</b> : Move lift up/down<br><br>
                        <b>T G</b> : Move head up/down<br>

                        <h3>Driving:</h3>

                        <b>W A S D</b> : Drive Forwards / Left / Back / Right<br><br>
                        <b>Shift</b> : Drive faster<br><br>

                        <button id="buttonUserCooperated" onClick=buttonUserCooperatedClicked(this) style="font-size: 14px">User cooperated</button>
                        <button id="buttonUserBetrayed" onClick=buttonUserBetrayedClicked(this) style="font-size: 14px">User betrayed Cozmo</button>
                        <button id="buttonTalk" onClick=buttonTalkClicked(this) style="font-size: 14px">Talk</button>
                        <button id="buttonToggleMode" onClick=buttonToggleModeClicked(this) style="font-size: 14px">Cooperating, click to change to: Mirror</button>
                    </td>
                    <td width=30></td>
                    <td valign=top>
                    </td>
                </tr>
            </table>

            <script type="text/javascript">
                var cozmoIsInCooperateMode = true
                var gLastClientX = -1
                var gLastClientY = -1
                var gIsMouseLookEnabled = false
                var gAreDebugAnnotationsEnabled = false
                var gIsHeadlightEnabled = false
                var gIsFreeplayEnabled = false
                var gIsDeviceGyroEnabled = false
                var gUserAgent = window.navigator.userAgent;
                var gIsMicrosoftBrowser = gUserAgent.indexOf('MSIE ') > 0 || gUserAgent.indexOf('Trident/') > 0 || gUserAgent.indexOf('Edge/') > 0;
                var gSkipFrame = false;

                if (gIsMicrosoftBrowser) {
                    document.getElementById("cozmoImageMicrosoftWarning").style.display = "block";
                }

                function postHttpRequest(url, dataSet)
                {
                    var xhr = new XMLHttpRequest();
                    xhr.open("POST", url, true);
                    xhr.send( JSON.stringify( dataSet ) );
                }

                function updateCozmo()
                {
                    if (gIsMicrosoftBrowser && !gSkipFrame) {
                        // IE doesn't support MJPEG, so we need to ping the server for more images.
                        // Though, if this happens too frequently, the controls will be unresponsive.
                        gSkipFrame = true;
                        document.getElementById("cozmoImageId").src="cozmoImage?" + (new Date()).getTime();
                    } else if (gSkipFrame) {
                        gSkipFrame = false;
                    }
                    var xhr = new XMLHttpRequest();
                    xhr.onreadystatechange = function() {
                        if (xhr.readyState == XMLHttpRequest.DONE) {
                            //document.getElementById("DebugInfoId").innerHTML = xhr.responseText
                        }
                    }

                    xhr.open("POST", "updateCozmo", true);
                    xhr.send( null );
                    setTimeout(updateCozmo , 60);
                }
                setTimeout(updateCozmo , 60);

                function updateButtonEnabledText(button, isEnabled)
                {
                    button.firstChild.data = isEnabled ? "Enabled" : "Disabled";
                }

                function buttonUserCooperatedClicked(button)
                {
                    
                    var xhr = new XMLHttpRequest();
                    var oldtext = document.getElementById("DebugInfoId").innerHTML + "<br>"
                    xhr.onreadystatechange = function() {
                        if (xhr.readyState == XMLHttpRequest.DONE) {
                            document.getElementById("DebugInfoId").innerHTML = oldtext + xhr.responseText
                        }
                    }

                    xhr.open("POST", "user_cooperates");
                    xhr.send( null );
                }

                function buttonUserBetrayedClicked(button)
                {
                    
                    var xhr = new XMLHttpRequest();
                    var oldtext = document.getElementById("DebugInfoId").innerHTML + "<br>"
                    xhr.onreadystatechange = function() {
                        if (xhr.readyState == XMLHttpRequest.DONE) {
                            document.getElementById("DebugInfoId").innerHTML = oldtext + xhr.responseText
                        }
                    }

                    xhr.open("POST", "user_betrays");
                    xhr.send( null );
                }

                function buttonTalkClicked(button)
                {
                    postHttpRequest("talk")
                }

                function buttonToggleModeClicked(button)
                {
                    var xhr = new XMLHttpRequest();
                    var oldtext = document.getElementById("DebugInfoId").innerHTML + "<br>"
                    xhr.onreadystatechange = function() {
                        if (xhr.readyState == XMLHttpRequest.DONE) {
                            document.getElementById("DebugInfoId").innerHTML = oldtext + xhr.responseText
                        }
                    }

                    xhr.open("POST", "change_cooperation_setting");
                    xhr.send( null );
                }

                function handleDropDownSelect(selectObject)
                {
                    selectedIndex = selectObject.selectedIndex
                    itemName = selectObject.name
                    postHttpRequest("dropDownSelect", {selectedIndex, itemName});
                }

                function handleKeyActivity (e, actionType)
                {
                    var keyCode  = (e.keyCode ? e.keyCode : e.which);
                    var hasShift = (e.shiftKey ? 1 : 0)
                    var hasCtrl  = (e.ctrlKey  ? 1 : 0)
                    var hasAlt   = (e.altKey   ? 1 : 0)

                    if (actionType=="keyup")
                    {
                        if (keyCode == 76) // 'L'
                        {
                            // Simulate a click of the headlight button
                            onHeadlightButtonClicked(document.getElementById("headlightId"))
                        }
                    }

                    postHttpRequest(actionType, {keyCode, hasShift, hasCtrl, hasAlt})
                }

                document.addEventListener("keydown", function(e) { handleKeyActivity(e, "keydown") } );
                document.addEventListener("keyup",   function(e) { handleKeyActivity(e, "keyup") } );

                function stopEventPropagation(event)
                {
                    if (event.stopPropagation)
                    {
                        event.stopPropagation();
                    }
                    else
                    {
                        event.cancelBubble = true
                    }
                }
            </script>

        </body>
    </html>
    '''