function openFriend(evt, FriendName) {

    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(FriendName).style.display = "block";
    evt.currentTarget.className += " active";

    document.getElementById("receiver").value = FriendName
  }
  
// Set the current user selected friend
var current_chat_select = document.getElementById("CurrentOpen");
if (!current_chat_select) {
  for (i = 0; i < current_chat_select.length; i++) {
    current_chat_select[i].className += " active";
  }
}
