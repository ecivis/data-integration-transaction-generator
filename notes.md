## Chalice Deploy with Custom Hostname
First grab the hosted zone identifier for dev.ecivis.com; it's needed later.
```shell
export AWS_PROFILE=ecivis_non_prod
export AWS_DEFAULT_REGION=us-west-2
api_hostname="ditg.dev.ecivis.com"

hosted_zone_id=$(aws route53 list-hosted-zones-by-name --dns-name dev.ecivis.com | \
  jq -r '.HostedZones[] | select(.Name=="'$api_hostname'.") | .Id' | grep -o -E '[^/]+$')
```
Create the certificate in ACM. Make note of the certificate ARN and update the `.chalice/config.json`
```shell
certificate_arn=$(aws acm request-certificate --domain-name "$api_hostname" \
    --validation-method DNS --idempotency-token 1234 \
    --options CertificateTransparencyLoggingPreference=ENABLED \
    --output text --query CertificateArn)
echo "certificate_arn: $certificate_arn"

validation_name=$(aws acm describe-certificate --certificate-arn $certificate_arn | jq -r '.Certificate.DomainValidationOptions[0].ResourceRecord.Name')
validation_value=$(aws acm describe-certificate --certificate-arn $certificate_arn | jq -r '.Certificate.DomainValidationOptions[0].ResourceRecord.Value')
aws route53 change-resource-record-sets --hosted-zone-id $hosted_zone_id --change-batch \
'{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "'$validation_name'",
        "Type": "CNAME",
        "TTL": 60,
        "ResourceRecords": [{"Value": "'$validation_value'"}]
      }
    }
  ]
}'
```

Deploy the API Gateway changes. Make note of the `HostedZoneId` and `AliasDomainName` returned. Create the ALIAS record in Route 53.
```shell
chalice deploy

alias_domain_name=""
alias_target_hosted_zone_id=""
aws route53 change-resource-record-sets --hosted-zone-id $hosted_zone_id --change-batch \
'{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "'$api_hostname'",
        "Type": "A",
        "AliasTarget": {
          "DNSName": "'$alias_domain_name'",
          "HostedZoneId": "'$alias_target_hosted_zone_id'",
          "EvaluateTargetHealth": false
        }
      }
    }
  ]
}'

```
