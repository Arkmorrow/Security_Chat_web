//generator private and public key when user is registered
var crypto = window.crypto || window.msCrypto;

// Generator keys and reutrn public key
async function genKeyPair() {
  const user_keys = await crypto.subtle.generateKey({name:"ECDH", namedCurve: "P-256"}, true, ["deriveKey"]);
  const exportKey = await crypto.subtle.exportKey("jwk", user_keys.publicKey)
  return JSON.stringify(exportKey);
}


let user_keys = genKeyPair()

//Give the user public key to the server
document.getElementById("user_public_key_id").value = user_keys;