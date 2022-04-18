//generator private and public key when user is registered
var crypto = window.crypto || window.msCrypto;

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

async function exportKey(k) {
  return JSON.stringify(await crypto.subtle.exportKey("jwk", k));
}


// Generator keys and reutrn public key
async function genKey() {
  const user_keys = await crypto.subtle.generateKey({name:"ECDH", namedCurve: "P-256"}, true, ["deriveKey"]);
  return user_keys;
}

async function run() {
  // Store the public key in the server

  const user_pub_key = await genKey()
  //const user_prv_key = await genKey()
  //var before_pub = localStorage.getItem("abcpub")

  /*if (before_pub != null) {
    const import_testing_pub = await crypto.subtle.importKey("jwk", JSON.parse(before_pub), {name:"ECDH", namedCurve: "P-256"}, true, [])
    const import_testing = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem("abc")), {name:"ECDH", namedCurve: "P-256"}, true, ["deriveKey"])

    let alicesSecretKey = await deriveSecretKey(import_testing, user_pub_key.publicKey);
    console.log((await exportKey(alicesSecretKey)));

    // Bob generates the same secret key using his private key and Alice's public key.
    let bobsSecretKey = await deriveSecretKey(user_pub_key.privateKey, import_testing_pub);
    console.log((await exportKey(bobsSecretKey)));
    //document.getElementById("user_public_key_id").value = await exportKey(alicesSecretKey);
    //document.getElementById("user_private_key_id").value = await exportKey(bobsSecretKey)
  }*/

  

  //const export_test = await exportKey(user_pub_key.privateKey)
  //localStorage.setItem("testing", export_test);
  //const import_testing = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem("testing")), {name:"ECDH", namedCurve: "P-256"}, true, ["deriveKey"])

  //let alicesSecretKey = await deriveSecretKey(import_testing, user_prv_key.publicKey);
  //console.log((await exportKey(alicesSecretKey)));

  // Bob generates the same secret key using his private key and Alice's public key.
  //let bobsSecretKey = await deriveSecretKey(user_prv_key.privateKey, user_pub_key.publicKey);
  //console.log((await exportKey(bobsSecretKey)));
  //document.getElementById("user_public_key_id").value = await exportKey(alicesSecretKey);
  //document.getElementById("user_private_key_id").value = await exportKey(bobsSecretKey)
  document.getElementById("user_public_key_id").value = await exportKey(user_pub_key.publicKey);
  document.getElementById("user_private_key_id").value = await exportKey(user_pub_key.privateKey);
}

run()