# python-trap-receiver-for-vROps

Set the Username, Authentication Password and Privacy Password in the envvars.txt file prior to running the script.<br />
Create and outbound SNMP plugin in vROps like in the following image:

![vROpsSNMPconf](https://user-images.githubusercontent.com/39626036/151814901-46467ca8-fc3b-423b-a417-efeaecb8bae1.png)

Create a custom notifcation rule in vROps which uses the vROps outbound SNMP plugin you just created.<br />
This rule will define what is sent to the script.<br /><br />

See the image below for example output of the script:
![exampleOutput](https://user-images.githubusercontent.com/39626036/151815913-3316287a-f45c-46e8-8526-4588f478887a.png)
