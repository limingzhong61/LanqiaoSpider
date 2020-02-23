var currentGPID = "T521"
var vcode = "int main() { return 0;}", vlang = "CPP";
$.post("/test.SubmitCode.dt", {gpid:currentGPID,lang:vlang,code:vcode}, function(obj){
    setData("lastlang", vlang);
    if (""+obj["ret"]=="1")
        window.location.href = "/status.page";
    else
        alert(obj["msg"]);
}, "json");