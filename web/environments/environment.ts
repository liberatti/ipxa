import packageJson from '../package.json';

export const environment = {
  name: packageJson.name,
  production: false,
  appContext: "/ipxa",
  apiUrl: `http://127.0.0.1:5000/ipxa`,
  apiDateFormat: "YYYY-MM-DDTHH:mm:ss.SSS[Z]",
  version: packageJson.version + "-dev"
};
