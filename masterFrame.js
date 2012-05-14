function destroyMasterFrame()  
{  
    master = document.getElementById("masterFrame"); 
    master.parentNode.removeChild(master); 
}

function initFraming() 
{ 

    //window.addEventListener("message", destroyMasterFrame, false); 

    masterFrame = document.createElement("IFRAME");                                
    masterFrame.setAttribute("src", "slaveFrame.js");                           
    masterFrame.setAttribute("id", "masterFrame");                               
    masterFrame.setAttribute("name", "masterFrame");                             
    masterFrame.setAttribute("height", "120");                                   
    masterFrame.setAttribute("width", "1200");                                    
    document.body.appendChild(masterFrame);
}

setTimeout("initFraming()",300);


