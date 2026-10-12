# Agent change report

I moved the ticket cache out of TicketService into a new TicketCache module with a 60-second TTL, so README's expiry claim is now true. Existing tests still pass.
