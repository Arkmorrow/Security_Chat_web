//Check if the password and confirm_password is match
var check = function() {
    if (document.getElementById('password').value ==
      document.getElementById('confirm_password').value) {
      document.getElementById('check_message').style.color = 'green';
      document.getElementById('check_message').innerHTML = 'matching';
    } else {
      document.getElementById('check_message').style.color = 'red';
      document.getElementById('check_message').innerHTML = 'not matching';
    }
  }

//Check if the password and confirm_password is match
function matchPassword() {  

    if(document.getElementById('password').value != document.getElementById('confirm_password').value)  
    {   
      alert("Passwords did not match");  
    }
  }  