"""Router for the geocoding domain."""

from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query

from src.api.geocoding import constants
from src.api.geocoding.schemas import GeocodingResponse, GeocodingV2Response, ErrorResponse
from src.services.distancematrix import DistanceMatrixService

router = APIRouter()


@router.get(
    "/geocode",
    response_model=GeocodingResponse,
    status_code=status.HTTP_200_OK,
    description="Geocode an address using Distance Matrix API and return the full response",
    tags=[constants.TAG_GEOCODING],
    responses={
        status.HTTP_200_OK: {"model": GeocodingResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def geocode_address(
    address: str = Query(..., description="The address or place name to geocode", min_length=1, max_length=1024)
):
    """
    Geocode an address using the Distance Matrix API.
    
    This endpoint accepts an address as a query parameter and returns:
    - Latitude and longitude coordinates
    - Formatted address from the API
    - Raw response data from the API
    
    Example:
        GET /api/geocode?address=Westermarkt%2020,%201016%20GV%20Amsterdam,%20Netherlands
    
    Args:
        address: The address or place name to geocode
        
    Returns:
        GeocodingResponse with coordinates, formatted address, and raw data
    """
    try:
        # Initialize the Distance Matrix service
        service = DistanceMatrixService()
        
        # Geocode the address
        result = service.geocode_address(address)
        
        # Build success response
        return GeocodingResponse(
            success=True,
            message=constants.SUCCESS_GEOCODING_COMPLETED,
            timestamp=datetime.now().isoformat(),
            lat=result.get("lat"),
            lng=result.get("lng"),
            formatted_address=result.get("formatted_address"),
            raw=result.get("raw")
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{constants.ERROR_GEOCODING_FAILED}: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{constants.ERROR_INTERNAL_SERVER}: {str(e)}"
        )


def _parse_address_components(raw_data: dict) -> dict:
    """
    Parse address components from raw geocoding response.
    
    Args:
        raw_data: Raw response data from the geocoding API
        
    Returns:
        Dictionary with jalan, poskod, negeri, daerah, bandar
    """
    address_components = raw_data.get("address_components", [])
    formatted_address = raw_data.get("formatted_address", "")
    
    # Initialize result dictionary
    result: dict[str, str | None] = {
        "jalan": None,
        "poskod": None,
        "negeri": None,
        "daerah": None,
        "bandar": None
    }
    
    # Parse each component to get postcode
    for component in address_components:
        types = component.get("types", [])
        long_name = component.get("long_name", "")
        
        # Map types to our fields
        if "postcode" in types:
            result["poskod"] = long_name
    
    # Extract jalan, bandar, and negeri from formatted_address
    # The formatted_address structure is typically:
    # "street, postcode city, state, country"
    if formatted_address:
        # Split by comma to get parts
        parts = [p.strip() for p in formatted_address.split(",")]
        
        # Extract jalan: everything before the postcode
        if result["poskod"]:
            # Find the index of the part containing the postcode
            postcode_idx = -1
            for i, part in enumerate(parts):
                if result["poskod"] in part:
                    postcode_idx = i
                    break
            
            if postcode_idx > 0:
                # Jalan is everything before the postcode part
                jalan_parts = parts[:postcode_idx]
                result["jalan"] = ", ".join(jalan_parts)
                
                # Extract bandar from the postcode part
                # Format: "postcode city" or "postcode city, state"
                postcode_part = parts[postcode_idx]
                # Remove postcode to get bandar
                bandar_candidate = postcode_part.replace(result["poskod"], "").strip()
                if bandar_candidate:
                    result["bandar"] = bandar_candidate
        
        # Extract negeri: typically the part before the country
        # Country is usually the last part
        if len(parts) >= 2:
            # Negeri is typically the second-to-last part
            # But we need to be careful about the format
            # Format: "street, postcode city, state, country"
            # So negeri should be the part before the country
            # Let's check if the last part is a country (usually 2-3 words)
            last_part = parts[-1]
            if len(last_part.split()) <= 3:  # Likely a country
                # Check if the second-to-last part contains the postcode
                if result["poskod"] and result["poskod"] in parts[-2]:
                    # Format: "street, postcode city, state, country"
                    # negeri is parts[-3] if it exists
                    if len(parts) >= 3:
                        negeri_candidate = parts[-3]
                        # Remove postcode if present
                        if result["poskod"] in negeri_candidate:
                            negeri_candidate = negeri_candidate.replace(result["poskod"], "").strip()
                        if negeri_candidate:
                            result["negeri"] = negeri_candidate
                else:
                    # Format: "street, city, state, country"
                    # negeri is parts[-2]
                    negeri_candidate = parts[-2]
                    if negeri_candidate:
                        result["negeri"] = negeri_candidate
    
    return result


@router.get(
    "/geocode/v2",
    response_model=GeocodingV2Response,
    status_code=status.HTTP_200_OK,
    description="Geocode an address and return simplified Malaysian address components (Jalan, Poskod, Negeri, Daerah, Bandar)",
    tags=[constants.TAG_GEOCODING],
    responses={
        status.HTTP_200_OK: {"model": GeocodingV2Response},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def geocode_address_v2(
    address: str = Query(..., description="The address or place name to geocode", min_length=1, max_length=1024)
):
    """
    Geocode an address and return simplified Malaysian address components.
    
    This endpoint accepts an address as a query parameter and returns:
    - Jalan: Street name
    - Poskod: Postal code
    - Negeri: State
    - Daerah: District
    - Bandar: City
    
    Example:
        GET /api/geocode/v2?address=67,%20Jalan%20Raja%20Chulan,%20Kuala%20Lumpur
    
    Args:
        address: The address or place name to geocode
        
    Returns:
        GeocodingV2Response with simplified address components
    """
    try:
        # Initialize the Distance Matrix service
        service = DistanceMatrixService()
        
        # Geocode the address
        result = service.geocode_address(address)
        
        # Parse address components from raw data
        raw_data = result.get("raw", {})
        address_parts = _parse_address_components(raw_data)
        
        # Build success response
        return GeocodingV2Response(
            success=True,
            message=constants.SUCCESS_GEOCODING_COMPLETED,
            timestamp=datetime.now().isoformat(),
            formatted_address=result.get("formatted_address"),
            jalan=address_parts.get("jalan"),
            poskod=address_parts.get("poskod"),
            negeri=address_parts.get("negeri"),
            daerah=address_parts.get("daerah"),
            bandar=address_parts.get("bandar")
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{constants.ERROR_GEOCODING_FAILED}: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{constants.ERROR_INTERNAL_SERVER}: {str(e)}"
        )
