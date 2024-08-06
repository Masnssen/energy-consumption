import React from 'react';

const DateRangeSelection = ({ onDateChange, errors }) => {
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  return (
    <div className="date-range-picker">
      <h3>Select Date and Time Range</h3>
      <div className='Select_dateTime'>
        <div>
          <label htmlFor="start-datetime">Start Date and Time:</label>
          <input
            type="datetime-local"
            id="start-datetime"
            onChange={(e) => onDateChange('start', e.target.value)}
            className={errors.start ? 'error-border' : ''}
          />
          {errors.start && <span className="error-message">{errors.start}</span>} 
        </div>
        <div>
          <label htmlFor="end-datetime">End Date and Time:</label>
          <input
            type="datetime-local"
            id="end-datetime"
            onChange={(e) => onDateChange('end', e.target.value)}
            className={errors.end ? 'error-border' : ''}
          />
          {errors.end && <span className="error-message">{errors.end}</span>}
        </div>
        
      </div>
    
      <div className="timezone-info">
        <p>Note: The selected dates and times are in the following timezone:</p>
        <strong>{timezone}</strong>
      </div>

    </div>
  );
};


export default DateRangeSelection;
