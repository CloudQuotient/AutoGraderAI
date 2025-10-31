import { CognitoUserPool } from 'amazon-cognito-identity-js';

// Get these values from your AWS Cognito console
const poolData = {
  UserPoolId: 'us-east-1_PsdG9pvLq', // Your User Pool ID
  ClientId: '6pg5hfcs2gnnr6p7ik7pgoli5q'        // Your App Client ID
};

export const userPool = new CognitoUserPool(poolData);