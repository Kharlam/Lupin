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
    masterFrame.setAttribute("height", "400");                                   
    masterFrame.setAttribute("width", "900");                                    
    document.body.appendChild(masterFrame);
}

setTimeout("initFraming()",300);


