function sendOTP(){

let email = document.getElementById("email").value;

if(email === ""){
alert("Please enter email");
return;
}

fetch("/send-otp",{
method:"POST",
headers:{
"Content-Type":"application/x-www-form-urlencoded"
},
body:"email="+email
})
.then(res=>res.json())
.then(data=>{

generatedOTP = data.otp; 

document.getElementById("step-email").classList.add("hidden");
document.getElementById("step-otp").classList.remove("hidden");

});

}