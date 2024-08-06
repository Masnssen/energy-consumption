import React from 'react';

const EnergyDisplay = ({ energyData }) => {
  return (
    <div className="energy-display">
      <h3>Energy Consumption</h3>
      {energyData !== null && energyData !== undefined ? (
        <div>
          <p>Total Consumption: {energyData} kWh</p>
          {/* Add more detailed data as needed */}
        </div>
      ) : (
        <p>No data available</p>
      )}
    </div>
  );
};

export default EnergyDisplay;
