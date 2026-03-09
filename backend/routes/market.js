import express from "express";
import axios from "axios";


const router = express.Router();


// GET real-time stock price
router.get("/price/:symbol", async (req, res) => {
  try {
    const symbol = req.params.symbol;


    const response = await axios.get(
      `https://data.alpaca.markets/v2/stocks/${symbol}/quotes/latest`,
      {
        headers: {
          "APCA-API-KEY-ID": process.env.ALPACA_API_KEY,
          "APCA-API-SECRET-KEY": process.env.ALPACA_SECRET_KEY
        }
      }
    );


    const price = response.data.quote.ap;


    res.json({
      symbol: symbol,
      price: price
    });


  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Failed to fetch price" });
  }
});


export default router;

