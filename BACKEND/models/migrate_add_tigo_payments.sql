-- Run this if your database already exists and needs Tigo payment methods
ALTER TABLE payments DROP CONSTRAINT IF EXISTS payments_payment_method_check;
ALTER TABLE payments ADD CONSTRAINT payments_payment_method_check 
    CHECK (payment_method IN ('airtel', 'vodacom', 'tigo', 'tigopesa', 'halotel', 'yas', 'cash', 'bank_transfer'));
