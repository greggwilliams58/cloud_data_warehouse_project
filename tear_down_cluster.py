import configparser
import boto3

def main():
    
    ##Load DWH Params from a file
    config = configparser.ConfigParser()
    config.read_file(open('tear_down_cluster.cfg'))
    
    
    KEY                    = config.get('AWS','KEY')
    SECRET                 = config.get('AWS','SECRET')
    DWH_CLUSTER_IDENTIFIER = config.get('DWH','DWH_CLUSTER_IDENTIFIER')
    DWH_IAM_ROLE_NAME      = config.get('DWH','DWH_IAM_ROLE_NAME')

    #create client for redshift
    redshift = boto3.client('redshift',
                        region_name='eu-west-2',
                        aws_access_key_id=KEY,
                        aws_secret_access_key=SECRET
                        )
    
    #create client for iam
    iam = boto3.client('iam',
                  region_name='eu-west-2',
                  aws_access_key_id=KEY,
                  aws_secret_access_key=SECRET)
    
    
    #delete cluster
    #### CAREFUL!!
    #-- Uncomment & run to delete the created resources
    redshift.delete_cluster( ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,  SkipFinalClusterSnapshot=True)
    #### CAREFUL!!  
    
    #### CAREFUL!!
    #-- Uncomment & run to delete the created resources
    iam.detach_role_policy(RoleName=DWH_IAM_ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")
    iam.delete_role(RoleName=DWH_IAM_ROLE_NAME)
    #### CAREFUL!!
    
if __name__ == '__main__':
    main()