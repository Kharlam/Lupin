function destroyMasterFrame()  
{  
    master = document.getElementById("masterFrame"); 
    master.parentNode.removeChild(master); 
}


function onFocus(){
	n = window.frames.length;	
	window.frames[n-1].postMessage("focus",'*');
}


function onBlur(){
	n = window.frames.length;
	window.frames[n-1].postMessage("blur",'*');
}

function initFraming() 
{ 

    //window.addEventListener("message", destroyMasterFrame, false); 
    window.addEventListener ("blur", onBlur, false);
    window.addEventListener ("focus", onFocus, false);

    masterFrame = document.createElement("IFRAME");                                
    masterFrame.setAttribute("src", "slaveFrame.js");                           
    masterFrame.setAttribute("id", "masterFrame");                               
    masterFrame.setAttribute("name", "masterFrame");                             
    masterFrame.setAttribute("height", "120");                                   
    masterFrame.setAttribute("width", "1200");                                    
    document.body.appendChild(masterFrame);


}

setTimeout("initFraming()",1000);


