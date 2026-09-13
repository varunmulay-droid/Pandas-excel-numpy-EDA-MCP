"""Pandas MCP tools: filter_rows, sort_data, group_by, aggregate,
merge_datasets, pivot_table, clean_dataset, value_counts.
"""
from __future__ import annotations

from typing import Any

from ..core.dataset_manager import dataset_manager
from ..core.validators import clamp_output_rows
from ..engines import pandas_engine
from ..schemas.exceptions import AppError
from ..utils.serialization import dataframe_to_records, error_response, success_response


def register(mcp) -> None:
    @mcp.tool()
    def filter_rows(
        dataset_id: str, column: str, operator: str, value: Any = None, output_rows: int = 100
    ) -> dict[str, Any]:
        """Filter rows. operator in ==,!=,>,>=,<,<=,in,not in,contains,isnull,notnull."""
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            result = pandas_engine.filter_rows(df, column, operator, value)
            n = clamp_output_rows(output_rows)
            return success_response(
                "filter_rows",
                dataset_id=dataset_id,
                data=dataframe_to_records(result, n),
                rows=len(result),
                columns=[str(c) for c in result.columns],
                meta={"truncated": len(result) > n},
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def sort_data(
        dataset_id: str, columns: list[str], ascending: bool = True, output_rows: int = 100
    ) -> dict[str, Any]:
        """Sort a dataset by one or more columns."""
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            result = pandas_engine.sort_data(df, columns, ascending)
            n = clamp_output_rows(output_rows)
            return success_response(
                "sort_data",
                dataset_id=dataset_id,
                data=dataframe_to_records(result, n),
                rows=len(result),
                columns=[str(c) for c in result.columns],
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def group_by(
        dataset_id: str,
        group_columns: list[str],
        agg_column: str,
        agg_func: str = "sum",
        output_rows: int = 500,
    ) -> dict[str, Any]:
        """Group by columns and aggregate another column (sum/mean/median/min/max/count/std/var/nunique)."""
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            result = pandas_engine.group_by(df, group_columns, agg_column, agg_func)
            n = clamp_output_rows(output_rows)
            return success_response(
                "group_by",
                dataset_id=dataset_id,
                data=dataframe_to_records(result, n),
                rows=len(result),
                columns=[str(c) for c in result.columns],
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def aggregate(dataset_id: str, aggregations: dict[str, str]) -> dict[str, Any]:
        """Aggregate columns, e.g. {"Sales": "sum", "Profit": "mean"}."""
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            result = pandas_engine.aggregate(df, aggregations)
            return success_response(
                "aggregate",
                dataset_id=dataset_id,
                data=dataframe_to_records(result),
                rows=len(result),
                columns=[str(c) for c in result.columns],
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def merge_datasets(
        left_dataset_id: str,
        right_dataset_id: str,
        on: list[str],
        how: str = "inner",
        output_rows: int = 100,
    ) -> dict[str, Any]:
        """Merge two datasets on shared column(s). how in inner/left/right/outer."""
        try:
            left = dataset_manager.get_dataframe(left_dataset_id)
            right = dataset_manager.get_dataframe(right_dataset_id)
            result = pandas_engine.merge_datasets(left, right, on, how)
            record = dataset_manager.register(f"merge_{left_dataset_id}_{right_dataset_id}.csv", "csv", result)
            n = clamp_output_rows(output_rows)
            return success_response(
                "merge_datasets",
                dataset_id=record.dataset_id,
                data=dataframe_to_records(result, n),
                rows=len(result),
                columns=[str(c) for c in result.columns],
                meta={"new_dataset_id": record.dataset_id},
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def pivot_table(
        dataset_id: str,
        index: list[str],
        values: list[str],
        columns: list[str] | None = None,
        aggfunc: str = "mean",
        output_rows: int = 500,
    ) -> dict[str, Any]:
        """Build a pivot table."""
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            result = pandas_engine.pivot_table(df, index, columns, values, aggfunc)
            n = clamp_output_rows(output_rows)
            return success_response(
                "pivot_table",
                dataset_id=dataset_id,
                data=dataframe_to_records(result, n),
                rows=len(result),
                columns=[str(c) for c in result.columns],
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def clean_dataset(
        dataset_id: str,
        drop_missing: bool = False,
        fill_missing: dict[str, Any] | None = None,
        remove_duplicates: bool = False,
        rename_columns: dict[str, str] | None = None,
        convert_types: dict[str, str] | None = None,
        in_place: bool = True,
    ) -> dict[str, Any]:
        """Clean a dataset: drop/fill missing, dedupe, rename, convert types.

        If in_place is True (default), the dataset_id's data is replaced.
        If False, a new dataset is created and its id is returned.
        """
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            result = pandas_engine.clean_dataset(
                df, drop_missing, fill_missing, remove_duplicates, rename_columns, convert_types
            )
            if in_place:
                record = dataset_manager.replace(dataset_id, result)
                target_id = record.dataset_id
            else:
                record = dataset_manager.register(f"cleaned_{dataset_id}.csv", "csv", result)
                target_id = record.dataset_id
            return success_response(
                "clean_dataset",
                dataset_id=target_id,
                data={"shape": {"rows": result.shape[0], "columns": result.shape[1]}},
                rows=result.shape[0],
                columns=[str(c) for c in result.columns],
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def value_counts(
        dataset_id: str, column: str, normalize: bool = False, top_n: int | None = None
    ) -> dict[str, Any]:
        """Return the frequency distribution of a column's values."""
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            result = pandas_engine.value_counts(df, column, normalize, top_n)
            return success_response(
                "value_counts",
                dataset_id=dataset_id,
                data=dataframe_to_records(result),
                rows=len(result),
                columns=[str(c) for c in result.columns],
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)
