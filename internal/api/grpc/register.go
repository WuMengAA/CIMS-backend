package grpc

import (
	"context"
	"log"

	"github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Client"
	"github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Enum"
	"github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Server"
	"github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Service"
	"github.com/MINIOpenSource/CIMS-backend/internal/service"
)

type ClientRegisterServer struct {
	Service.UnimplementedClientRegisterServer
	clientService *service.ClientService
}

func NewClientRegisterServer() *ClientRegisterServer {
	return &ClientRegisterServer{
		clientService: service.NewClientService(),
	}
}

func (s *ClientRegisterServer) Register(ctx context.Context, req *Client.ClientRegisterCsReq) (*Server.ClientRegisterScRsp, error) {
	log.Printf("Register request from: %s (%s)", req.ClientUid, req.ClientId)

	err := s.clientService.Register(req.ClientUid, req.ClientId)
	if err != nil {
		return &Server.ClientRegisterScRsp{
			Retcode: Enum.Retcode_ServerInternalError,
			Message: err.Error(),
		}, nil
	}

	return &Server.ClientRegisterScRsp{
		Retcode: Enum.Retcode_Registered,
		Message: "Success",
	}, nil
}

func (s *ClientRegisterServer) UnRegister(ctx context.Context, req *Client.ClientRegisterCsReq) (*Server.ClientRegisterScRsp, error) {
	log.Printf("UnRegister request from: %s", req.ClientUid)

	err := s.clientService.UnRegister(req.ClientUid)
	if err != nil {
		return &Server.ClientRegisterScRsp{
			Retcode: Enum.Retcode_ServerInternalError,
			Message: err.Error(),
		}, nil
	}

	return &Server.ClientRegisterScRsp{
		Retcode: Enum.Retcode_Success,
		Message: "Success",
	}, nil
}
