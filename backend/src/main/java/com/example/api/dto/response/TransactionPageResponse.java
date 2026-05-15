package com.example.api.dto.response;

import java.util.List;

public record TransactionPageResponse(
        List<TransactionResponse> rows,
        long total,
        int page,
        int pageSize,
        int totalPages
) {}