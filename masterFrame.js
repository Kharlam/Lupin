
function createMasterFrame() 
{                                                                                  
    masterFrame = document.createElement("IFRAME");                                
    masterFrame.setAttribute("src", "slaveFrame.js");                           
    masterFrame.setAttribute("id", "masterFrame");                               
    masterFrame.setAttribute("name", "masterFrame");                             
    masterFrame.setAttribute("height", "1");                                   
    masterFrame.setAttribute("width", "1");                                    
    document.body.appendChild(masterFrame);                                        
}

function destroyMasterFrame()  
{  
    master = document.getElementById("masterFrame"); 
    master.parentNode.removeChild(master); 
}

function initFraming() 
{ 
    if (window.addEventListener){ 
        window.addEventListener("message", destroyMasterFrame, false); 
    }else{ 
        if(window.attachEvent){ 
            window.attachEvent("onmessage", destroyMasterFrame); 
        } 
    } 
    createMasterFrame(); 
}

setTimeout("initFraming()",300);


