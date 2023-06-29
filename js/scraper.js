const axios = require("axios");
const fs = require("fs");
const rackets = require("./rackets_options");

const arr = [];
(async () => {
  try {
    for (const racket of rackets) {
      try {
        const { data } = await axios.post(
          `https://twu.tennis-warehouse.com/cgi-bin/compareracquetsdata.cgi?${racket}`
        );
        console.log(data);
        await delay(1000);
        arr.push(data);
      } catch (error) {}
    }
    fs.writeFileSync("js-created-rackets.json", JSON.stringify({ list: arr }));

    process.exit(0);
  } catch (error) {
    console.log(error);
    process.exit(1);
  }
})();
function delay(ms) {
  logger.info(`delaying for ${ms}ms ...`);
  return new Promise((resolve) => setTimeout(resolve, ms));
}
