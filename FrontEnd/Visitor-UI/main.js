function service(x) {
  console.log(x);
  callAws(x);
}

function callAws(x) {
  var apigClient = apigClientFactory.newClient({
    accessKey: "AKIAJPNIFMVLMBC3LPAQ",
    secretKey: "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",
    region: "us-west-2"
  });
  let params = {};
  var body = {
    message: x
  };
  apigClient
    .valPost(params, body)
    .then(function(result) {
      z = result.data.statusCode;
      if(z==400)alert(
        "Invalid OTP"
      );
      
      else 
      alert("Welcome " + result.data.body.visitorName);
      console.log(result.data.body);
    })
    .catch(function(result) {
      console.log(result);
    });
}


