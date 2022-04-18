//encrypt the message
var crypto = window.crypto || window.msCrypto;
//let iv,ciphertext
function convertArrayBufferToBase64(arrayBuffer) {
  return btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
}

async function exportKey(k) {
  return JSON.stringify(await crypto.subtle.exportKey("jwk", k));
}

function convertBase64ToArrayBuffer(base64) {
  return (new Uint8Array(atob(base64).split('').map(char => char.charCodeAt()))).buffer;
}
function deriveSecretKey(privateKey, publicKey) {
    return crypto.subtle.deriveKey(
      {
        name: "ECDH",
        public: publicKey
      },
      privateKey,
      {
        name: "AES-GCM",
        length: 256
      },
      true,
      ["encrypt", "decrypt"]
    );
  }

  async function encrypt(secretKey, messages_need) {

    iv = window.crypto.getRandomValues(new Uint8Array(12));
    let enc = new TextEncoder();

    var encoded = enc.encode(messages_need);

    ciphertext = await window.crypto.subtle.encrypt(
      {
        name: "AES-GCM",
        iv: iv
      },
      secretKey,
      encoded
    );

  }

  /*
  Decrypt the message using the secret key.
  If the ciphertext was decrypted successfully,
  update the "decryptedValue" box with the decrypted value.
  If there was an error decrypting,
  update the "decryptedValue" box with an error message.
  */
  async function decrypt(secretKey) {

    let decrypted = await window.crypto.subtle.decrypt(
      {
        name: "AES-GCM",
        iv: iv
      },
      secretKey,
      ciphertext
    );

    let dec = new TextDecoder();

    console.log(dec.decode(decrypted));

  }

  async function agreeSharedSecretKey(messages_need) {
    // Generate 2 ECDH key pairs: one for Alice and one for Bob
    // In more normal usage, they would generate their key pairs
    // separately and exchange public keys securely

    var username = document.getElementById("CurrentOpen")


    if (username != null) {
      username = document.getElementById("CurrentOpen").innerHTML
    }

    var temp_tab = document.getElementById(username)

    var abc_pk = temp_tab.getElementsByClassName("receiver_pk")[0].value
    var abcd_pks = temp_tab.getElementsByClassName("current_user_pk")[0].value
    localStorage.setItem("receiver_pk",abc_pk);
    localStorage.setItem("current_user_pk",abcd_pks);

    // Import public key
    const abc_pubkey = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem("current_user_pk")), {name:"ECDH", namedCurve: "P-256"}, true, [])

    //get current user private key from localStorage
    const abc_sekey = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem("abc")), {name:"ECDH", namedCurve: "P-256"}, true, ["deriveKey"])

    // Import public key
    const abcd_pubkey = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem("receiver_pk")), {name:"ECDH", namedCurve: "P-256"}, true, [])

    //get current user private key from localStorage
    const abcd_sekey = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem("abcd")), {name:"ECDH", namedCurve: "P-256"}, true, ["deriveKey"])

    // Alice then generates a secret key using her private key and Bob's public key.
    let abcSecretKey = await deriveSecretKey(abc_sekey, abcd_pubkey);

    // Bob generates the same secret key using his private key and Alice's public key.
    let abcdSecretKey = await deriveSecretKey(abcd_sekey, abc_pubkey);

    console.log((await exportKey(abcdSecretKey)));
    console.log((await exportKey(abcSecretKey)));

    // Alice can then use her copy of the secret key to encrypt a message to Bob.
    encrypt(abcSecretKey, messages_need);
    await new Promise(resolve => setTimeout(resolve, 500));
    decrypt(abcdSecretKey);
  }

//Get user private key store in the localStorage
async function encrypts_msg(username, iv, messages_need) {

    // Import public key
    const receiver_pubkey = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem("receiver_pk")), {name:"ECDH", namedCurve: "P-256"}, true, [])

    //get current user private key from localStorage
    const current_sekey = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem(username)), {name:"ECDH", namedCurve: "P-256"}, true, ["deriveKey"])
    

    // Get the shared key
    const encrypt_key = await deriveSecretKey(current_sekey, receiver_pubkey);
    

    let enc = new TextEncoder();

    var encoded = enc.encode(messages_need);

    return await window.crypto.subtle.encrypt(
        {
          name: "AES-GCM",
          iv: iv
        },
        encrypt_key,
        encoded
      ); 
}

//Get user private key store in the localStorage
async function decrypt_msg(username, pub_key, message, iv, current_pk) {

  var current_user = document.getElementById("current_user_name").innerHTML

  // Import public key
  const receiver_pubkey = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem("receiver_pk")), {name:"ECDH", namedCurve: "P-256"}, true, [])

  //const current_pks = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem("current_user_pk")), {name:"ECDH", namedCurve: "P-256"}, true, [])
  //const current_se = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem("abcd")), {name:"ECDH", namedCurve: "P-256"}, true, ["deriveKey"])

  //get current user private key from localStorage
  const current_sekey = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem(current_user)), {name:"ECDH", namedCurve: "P-256"}, true, ["deriveKey"])
  

  // Get the shared key
  const encrypt_key = await deriveSecretKey(current_sekey, receiver_pubkey);

  //const encrypt_keys = await deriveSecretKey(current_se, current_pks);
  //console.log((await exportKey(encrypt_key)));
  //console.log((await exportKey(encrypt_keys)));


  return await window.crypto.subtle.decrypt(
      {
        name: "AES-GCM",
        iv: iv
      },
      encrypt_key,
      message
    );

  
}

function encrypt_msg(username, pub_key) {

    iv = window.crypto.getRandomValues(new Uint8Array(12));

    var messages_need = document.getElementById("messages").value

    var current_user = document.getElementById("current_user_name").innerHTML

    let test = encrypts_msg(current_user, iv, messages_need);

    test.then((val) => {

      var final_msg = {
      iv: convertArrayBufferToBase64(iv),
      encrypt_key: convertArrayBufferToBase64(val)
      }

      document.getElementById(username).getElementsByClassName("msg_encrypted")[0].value = JSON.stringify(final_msg);
    });

    

}

var username = document.getElementById("CurrentOpen")


if (username != null) {
  username = document.getElementById("CurrentOpen").innerHTML
}

var temp_tab = document.getElementById(username)
var current_user = document.getElementById("current_user_name").innerHTML

var user_pk = temp_tab.getElementsByClassName("receiver_pk")[0].value
var user_pks = temp_tab.getElementsByClassName("current_user_pk")[0].value
localStorage.setItem("receiver_pk",user_pk);
localStorage.setItem("current_user_pk",user_pks);


if (temp_tab != null) {
  var temp = temp_tab.getElementsByClassName("msg_need_changed")
  
  if (temp != null) {
    
    for (let i = 0; i < temp.length; i++) {
      var encrypt_info = JSON.parse(temp[i].innerHTML)

      console.log(temp[i].innerHTML);

      var iv = encrypt_info["iv"]

      var iv_rest = convertBase64ToArrayBuffer(iv)
      var encrypt_key = encrypt_info["encrypt_key"]

      var ret = convertBase64ToArrayBuffer(encrypt_key)

      var enc = new TextDecoder();
      var decrypt_msgs = decrypt_msg(username, user_pk, ret, iv_rest,user_pks)
      console.log(decrypt_msgs)
      decrypt_msgs.then((val) => {temp[i].innerHTML = enc.decode(val)})
      .catch(function(err){
        console.error(err);
    });
    }
    
  }
  
}

