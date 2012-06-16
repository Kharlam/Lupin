
function selfDestruct()
{
    master = document.getElementById("masterIframe"); 
    master.parentNode.removeChild(master); 
}

function onMessage(event)  
{  
    m = event.data;
    if("selfDestruct" == m){
    	selfDestruct();
    }

}

function onFocus()
{
	n = window.frames.length;	
	window.frames[n-1].postMessage("focus",'*');
}

function onBlur()
{
	n = window.frames.length;
	window.frames[n-1].postMessage("blur",'*');
}

function initFraming() 
{ 

    window.addEventListener("message", onMessage, false); 
    window.addEventListener ("blur", onBlur, false);
    window.addEventListener ("focus", onFocus, false);

    masterIframe = document.createElement("IFRAME");   
    masterIframe.setAttribute("src", _LUPIN_FRAME_TOKEN);                           
    masterIframe.setAttribute("id", "masterIframe");                               
    masterIframe.setAttribute("name", "masterIframe");                             
    masterIframe.setAttribute("height", "200");                                   
    masterIframe.setAttribute("width", "1200");                                    
    document.body.appendChild(masterIframe);

}

setTimeout("initFraming()",1000);


