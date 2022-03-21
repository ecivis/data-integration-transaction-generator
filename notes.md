## Chalice Deploy
```shell
export AWS_PROFILE=ecivis_non_prod
export AWS_DEFAULT_REGION=us-west-2

hosted_zone_id=$(aws route53 list-hosted-zones-by-name --dns-name dev.ecivis.com | \
  jq -r '.HostedZones[] | select(.Name=="dev.ecivis.com.") | .Id' | grep -o -E '[^/]+$')

chalice deploy

aws acm request-certificate --domain-name "ditg.dev.ecivis.com" \
    --validation-method DNS --idempotency-token 1234 \
    --options CertificateTransparencyLoggingPreference=DISABLED

# Update .chalice/config.json with ACM certificate ARN

# Create the certificate verification CNAME
aws route53 change-resource-record-sets \
    --hosted-zone-id $hosted_zone_id --change-batch \
'{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "_c08de96e2ad0641a94abec89e8a92d80.ditg.dev.ecivis.com.",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "_fd5200016689d4608dc590e00c302ee5.yyqgzzsvtj.acm-validations.aws."}]
      }
    }
  ]
}'

# Deploy the API Gateway changes
chalice deploy

# Create the Route 53 ALIAS for the API Gateway with values returned above
aws route53 change-resource-record-sets --hosted-zone-id $hosted_zone_id --change-batch \
'{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "ditg.dev.ecivis.com",
        "Type": "A",
        "AliasTarget": {
          "DNSName": "d-q2355xn8r3.execute-api.us-west-2.amazonaws.com",
          "HostedZoneId": "Z2OJLYMUO9EFXC",
          "EvaluateTargetHealth": false
        }
      }
    }
  ]
}'

```
